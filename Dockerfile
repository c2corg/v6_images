FROM docker.io/debian:jessie

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'APT::Install-Recommends "0";' > /etc/apt/apt.conf.d/50no-install-recommends
RUN echo 'APT::Install-Suggests "0";' > /etc/apt/apt.conf.d/50no-install-suggests

WORKDIR /var/www/

COPY requirements.txt ./
COPY requirements_pip.txt ./
COPY setup.py ./
COPY c2corg_images c2corg_images

RUN apt-get update \
 && apt-get -y upgrade \
 && apt-get install -y \
    python3 \
    ca-certificates \
    imagemagick \
    jpegoptim \
    python3-wand \
    optipng \
    librsvg2-bin \
    python3-pip \
    libpq5 \
    libpq-dev \
    python3-dev \
    gcc \
 && pip3 install -r requirements_pip.txt \
 && pip  install -r requirements.txt \
 && pip  install . \
 && py3compile -f . \
 && rm -fr .cache \
 && apt-get -y purge \
    python3-dev \
    libpq-dev \
    gcc \
 && apt-get -y --purge autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY scripts scripts
COPY tests tests

EXPOSE 8080

COPY /docker-entrypoint.sh /
COPY /docker-entrypoint.d/* /docker-entrypoint.d/
ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["gunicorn", "-w", "4", "-u", "www-data", "-g", "www-data", "-b", "0.0.0.0:8080", "c2corg_images:app"]
