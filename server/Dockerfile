# FROM node:14.14.0-alpine
# WORKDIR /app
# COPY ./package.json ./
# RUN npm i
# COPY . .
# CMD ["npm", "run", "start"]

FROM python:alpine3.10

RUN apk add build-base

WORKDIR /app

ENV FLASK_APP = app.py

RUN apk --update add libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl

RUN apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

RUN pip install Pillow

# ENV FLASK_ENV = development
COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN python3 -m nltk.downloader wordnet

RUN python3 -m nltk.downloader omw-1.4

RUN python3 -m nltk.downloader punkt

RUN python3 -m nltk.downloader stopwords

COPY . .

# CMD ["python", "app.py"]
CMD ["gunicorn", "--workers=2", "--chdir=.", "--bind", "0.0.0.0:5000", "--access-logfile=-", "--error-logfile=-", "app:app"]
