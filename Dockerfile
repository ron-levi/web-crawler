FROM python:3

ADD web_crawler.py /

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY . /

CMD [ "python", "./web_crawler.py" ]












## Creating Application Source Code Directory
#RUN mkdir -p /usr/src/app
#
## Setting Home Directory for containers
#WORKDIR /usr/src/app
#
## Installing python dependencies
#COPY requirements.txt /usr/src/app/
#RUN pip install --no-cache-dir -r requirements.txt
#
## Copying src code to Container
#COPY . /usr/src/app
#
## Running Python Application
#CMD gunicorn -b :$PORT -c gunicorn.conf.py main:app