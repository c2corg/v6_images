FROM docker.io/debian:jessie

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'APT::Install-Recommends "0";' > /etc/apt/apt.conf.d/50no-install-recommends
RUN echo 'APT::Install-Suggests "0";' > /etc/apt/apt.conf.d/50no-install-suggests

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
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/

COPY requirements.txt ./
COPY requirements_pip.txt ./
COPY setup.py ./
COPY c2corg_images c2corg_images
COPY scripts scripts
COPY tests tests

RUN pip3 install -r requirements_pip.txt && \
    pip  install -r requirements.txt && \
    pip  install . && \
    rm -fr .cache

RUN mkdir -p /var/www/incoming /var/www/active && \
    chown www-data:www-data /var/www/incoming /var/www/active

EXPOSE 8080
USER www-data
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "c2corg_images:app"]
