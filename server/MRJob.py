from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"[\w']+")

class Count(MRJob):

    def mapper(self, _, line):
        line = line.strip()
        
        for word in WORD_RE.findall(line):
            yield word.lower(), 1
            
    def reducer(self, word, counts):
        yield word, sum(counts)


"""the below 2 lines are ensuring the execution of mrjob, the program will not
execute without them"""
if __name__ == '__main__':
    Count.run()