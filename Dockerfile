FROM python:3

ADD web_crawler.py /

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY . /

CMD [ "python", "./web_crawler.py" ]

