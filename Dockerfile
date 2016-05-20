FROM debian:jessie
MAINTAINER info@camptocamp.com

RUN apt-get update && apt-get install -y \
  python3 \
  wget \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /root/
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY setup.py ./
COPY c2cv6images c2cv6images
RUN python3 setup.py install --user

EXPOSE 80
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "c2cv6images:app"]
