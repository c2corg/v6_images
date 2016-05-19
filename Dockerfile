FROM debian:jessie
MAINTAINER info@camptocamp.com

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y wget

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY c2cv6images.py .

EXPOSE 80
CMD gunicorn -w 4 -b 0.0.0.0:80 c2cv6images:app
