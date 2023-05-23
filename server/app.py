import redis
# from crypt import methods
from flask_cors import CORS
from flask import Flask, jsonify, request
import pymongo
import boto3
from botocore.config import Config
import nltk
import threading
import time
import tempfile
import os
# nltk.download('wordnet')
# nltk.download('omw-1.4')
# nltk.download('punkt')
# nltk.download('stopwords')
from nltk.corpus import wordnet, stopwords
import queue
import textract

app = Flask(__name__)
CORS(app)

S3_BUCKET = 'eccproject-iub'

myclient = pymongo.MongoClient("mongodb://admin:password@mongodb-test:27017/")
mydb = myclient["mydatabase"]
history = mydb["search_history"]
url_data = mydb["url_data"]
stats_col = mydb["statistics"]  # this is to create collection
uploaded_docs = mydb["uploaded_docs"]

# url_data.drop()
# history.drop()
# stats_col.drop()
# uploaded_docs.drop()

# cache = redis.Redis(host='localhost', port=6379, password="Pa$$w0rd")
cache = redis.Redis(host='redis', port=6379, password="ubuntu")

@app.route("/", methods=["GET"])
def test_server():
    return jsonify({"data":"Server working!"})

def update_redis_cache():
    print("started ....")
    history_data = history.find()
    # print(history_data)
    data = []
    for word_data in history_data:
        data.append((word_data["keyword"], word_data["search_count"]))
    sorted_history = sorted(data, key=lambda x: x[1], reverse=True)

    # update cache
    for keyword, search_count in sorted_history:
        # print(keyword)
        if search_count > 3:
            keyword_data = url_data.find_one({"_id": keyword.lower()})
            print("keyword_data", keyword_data)
            if keyword_data:
                if cache.exists(keyword.lower()):
                    cache.delete(keyword.lower())
                urls = [x["doc_name"] for x in keyword_data["s3_docs"]]
                print(urls)
                cache.rpush(keyword.lower(), *urls)
                cache.expire(keyword.lower(), 100)

    print("completed ....")

def get_urls(word, thread_q):
    to_return = []

    # if keyword is not present in cache, go to mongo
    if not cache.exists(word):
        print("in cache not exists")
        data_mongo = url_data.find_one({"_id": word})
        print("datamongo", data_mongo)
        if not data_mongo:
            print("Data not in mongo so relevent search")
            # Creating a list
            relevent_words_raw = []
            for syn in wordnet.synsets(word):
                for l in syn.lemmas():
                    relevent_words_raw.append(l.name())
                    if l.antonyms():
                        relevent_words_raw.append(l.antonyms()[0].name())
            relevent_words = list(set(relevent_words_raw))
            to_sort_urls = []
            for word in relevent_words:
                data_mongo = url_data.find_one({"_id": word})
                if data_mongo:
                    urls_list = data_mongo["s3_docs"]
                    for url_ in urls_list:
                        to_sort_urls.append(
                            (url_["doc_name"], url_["total_occurences"]))
            if to_sort_urls:
                sorted_urls = sorted(
                    to_sort_urls, key=lambda x: x[1], reverse=True)
                to_return = [x[0] for x in sorted_urls]
            else:
                to_return = []
        else:
            print("data in mongo so get data from mongo")
            urls_list = data_mongo["s3_docs"]
            to_sort_urls = []
            for url_ in urls_list:
                to_sort_urls.append(
                    (url_["doc_name"], url_["total_occurences"]))
            sorted_urls = sorted(
                to_sort_urls, key=lambda x: x[1], reverse=True)
            to_return = [x[0] for x in sorted_urls]
    else:
        # return if word is present in mongo
        data_in_cache = []
        print("data in cache")
        for item in cache.lrange(word, 0, -1):
            data_in_cache.append(item.decode())
        print("data_in_cache", data_in_cache)
        to_return = data_in_cache
    print("to_return", to_return)
    thread_q.put(to_return)

@app.route("/search", methods=["POST"]) 
def search():
    start = time.perf_counter()
    # get search from from reuqest body
    search_string = request.get_json()["search_string"]
    words_to_search = list(set(search_string.split(" ")))

    # update search history for every word from search history
    for word in words_to_search:
        print(word)
        # add the searched string to history
        ispresent = history.find_one({"keyword": word.lower()})
        # print(ispresent)
        if ispresent:
            history.update_one({"keyword": word.lower()}, {
                               "$set": {"search_count": (ispresent["search_count"]+1)}})
        else:
            history.insert_one({"keyword": word.lower(), "search_count": 1})
    # search string = cat likes cat, then search history for cat is updated twice... discuss this!!!!!

    final_toreturn = []
    thread_q = queue.Queue()

    # find urls for every word from search string
    for word in words_to_search:
        print("Parsed word", word.lower())
        thread = threading.Thread(target=get_urls, args=(word.lower(),thread_q))
        thread.start()
        thread.join()

    while not thread_q.empty():
        item = thread_q.get()
        print("item",item)
        final_toreturn.extend(list(set(item)))

    # update redis cache
    threading.Thread(target=update_redis_cache).start()
    end = time.perf_counter()
    print("time diff: " + str(end-start) + "second(s)")
    if final_toreturn:
        return jsonify({"success": True, "data": list(set(final_toreturn))})
    else:
        return jsonify({"success": False, "data": "No relevent URL found"})

def update_statistics(keywords_processed):
    try:
        stats_record = stats_col.find_one({'_id': 1})
        if stats_record:
            print('Updating the rec...')
            # stats_col.update_one({'_id': 1}, {'$set': {"documents_uploaded": (
            #     stats_record['documents_uploaded'] + 1), "keywords_processed": (
            #     stats_record['keywords_processed'] + keywords_processed)}})

            stats_col.update_one({'_id': 1}, {'$set': {"stats": {"documents_uploaded": (
                stats_record["stats"]['documents_uploaded'] + 1), "keywords_processed": (
                stats_record["stats"]['keywords_processed'] + keywords_processed)}}})
        else:
            print('Inserting the rec...')
            stats_col.insert_one(
                {'_id': 1, 'stats': {"documents_uploaded": 1,  "keywords_processed": keywords_processed}})
                
    except Exception as e:
        return jsonify({"update_statistics execption": str(e)})

@app.route("/get_statistics", methods=["GET"])
def get_statistics():
    try:
        max_word_search_count = 0
        max_searched_word = ""
        # ----------- Return stats -----------#
        for document in history.find():
            if document["search_count"] > max_word_search_count:
                max_word_search_count = document["search_count"]
                max_searched_word = document["keyword"]

        stats_record = stats_col.find_one({'_id': 1})
        if stats_record:
            #To get list of upladed s3 objects 
            s3_docs = uploaded_docs.find_one({'_id': "s3_objects"})
            if s3_docs:
                stats_record["s3_docs"] = s3_docs["s3_docs"]
            #To get list of upladed s3 objects end 

            print("stats_record", stats_record)
            stats_record["stats"]["max_searched_word"] = max_searched_word
            return jsonify({"success": True, "data": stats_record})
        else:
            return {"success": False, "data": "No statistics available"}
    except Exception as e:
        return jsonify({"success": False, "data": str(e)})

def run_map_reduce(s3_object_name):
    """
    urls used:
    S3
    https://stackoverflow.com/questions/36205481/read-file-content-from-s3-bucket-with-boto3
    MRJ:
    https://www.geeksforgeeks.org/hadoop-mrjob-python-library-for-mapreduce-with-example/
    Function to list files in a given S3 bucket
    """
    with app.app_context():
        try:
            print("inside run_map_reduce")
            session = boto3.Session(
                aws_access_key_id="my-access-key",
                aws_secret_access_key="my-secret-key"
            )

            s3 = session.resource('s3')
            document_name  = s3_object_name
            file_ext = document_name.split('.').pop()
            obj = s3.Object(S3_BUCKET, document_name)

            s3_file = tempfile.NamedTemporaryFile(suffix='.'+file_ext)
            obj.download_file(s3_file.name)
            file_content = textract.process(s3_file.name)

            # Reading the File as String With Encoding //errors='ignore'
            # file_content = obj.get()['Body'].read().decode(errors='ignore')
            file_content = file_content.decode()
            file_content = file_content.strip()
            # --------------------NLTK----------------------------------#

            # tokenizers can be used to find the words and punctuation in a string
            tokens = nltk.word_tokenize(file_content)

            filtered_tokens = [w.lower() for w in tokens if w.isalnum() and (
                not w.lower() in stopwords.words('english'))]

            # ----------- Run map rededuce on -----------#
            filtered_words_file = tempfile.NamedTemporaryFile()
            word_count_file = tempfile.NamedTemporaryFile()

            try:
                for word in filtered_tokens:
                    filtered_words_file.write(bytes(word + '\n', 'utf-8'))

                filtered_words_file.seek(0)
                os.system("python3 MRJob.py <" + filtered_words_file.name +
                        "> " + word_count_file.name + " -r local")

                # file1 = open('myfile.txt', 'r')
                lines = word_count_file.readlines()
                word_count = []
                keywords_processed = 0

                # Strips the newline character
                for line in lines:
                    keywords_processed += 1
                    line = line.strip()
                    word, count = line.decode("utf-8").split("\t")
                    word = word.strip('"')
                    word_count.append((word, document_name, count))

                    if url_data.find_one({'_id': word}):
                        url_data.update_one({'_id': word}, {'$push': {'s3_docs': {
                            "doc_name": document_name, "total_occurences": count}}})
                    else:
                        url_data.insert_one({'_id': word, 's3_docs': [
                            {"doc_name": document_name,  "total_occurences": count}]})

                # ----------- Return stats -----------#
                update_statistics(keywords_processed)
            finally:
                filtered_words_file.close()
                word_count_file.close()

        except Exception as e:
            print("------------------- Exception ----------------")
            print(e)
            return jsonify({"run_map_reduce execption": str(e)})


@app.route('/save_s3_object_name', methods=["POST"])
def save_s3_object_name():
    start = time.perf_counter()
    try:
        s3_object_name = request.get_json()["s3_object_name"]

        #to maintain a list of s3 objects
        s3_obj_name, extension   = request.get_json()["s3_object_name"].split(".")

        if uploaded_docs.find_one({'_id': "s3_objects"}):
            uploaded_docs.update_one({'_id': "s3_objects"}, {'$push': {'s3_docs': {
                "name": s3_obj_name, "extension": extension}}})
        else:
            uploaded_docs.insert_one({'_id': "s3_objects", 's3_docs': [
                {"name": s3_obj_name,  "extension": extension}]})
        #to maintain a list of s3 objects end

        print("s3_object_name", s3_object_name)
        # run_map_reduce(s3_object_name)
        threading.Thread(target=run_map_reduce, args=(s3_object_name,)).start()
        end = time.perf_counter()
        print("time diff: " + str(end-start) + "second(s)")
        return get_statistics()
    except Exception as e:
        return jsonify({"save_s3_object_name execption": str(e)})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)