FROM python:3.7-alpine
MAINTAINER Nicolas Inden <nicolas@inden.one>

WORKDIR /app

RUN apk add zlib-dev jpeg-dev build-base nodejs npm hugo

COPY requirements.txt ./
RUN pip install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

COPY editing-ui ./editing-ui

RUN cd editing-ui && npm install && npm run compile

EXPOSE 8080

ENTRYPOINT [ "python", "./editing-ui/src/py/run.py" ]
