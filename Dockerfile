FROM docker.io/debian:jessie

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get -y upgrade \
 && apt-get install -y \
    python3 \
    wget \
    imagemagick \
    jpegoptim \
    python3-wand \
    optipng \
    librsvg2-bin \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /root/
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && rm -f get-pip.py

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY setup.py ./
COPY c2corg_images c2corg_images
COPY scripts scripts
COPY tests tests

RUN pip install .

EXPOSE 80
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "c2corg_images:app"]
