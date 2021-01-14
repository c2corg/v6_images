FROM camptocamp/c2cwsgiutils:4

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'APT::Install-Recommends "0";' > /etc/apt/apt.conf.d/50no-install-recommends
RUN echo 'APT::Install-Suggests "0";' > /etc/apt/apt.conf.d/50no-install-suggests

RUN set -x \
 && apt-get update \
 && apt-get install -y \
    ca-certificates \
    imagemagick \
    jpegoptim \
    optipng \
    librsvg2-bin \
    fonts-liberation \
    gsfonts \
    texlive-fonts-extra \
    texlive-fonts-recommended \
    gsfonts-x11 \
    ttf-bitstream-vera \
    ttf-dejavu \
 && rm -fr .cache \
 && apt-get -y --purge autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt setup.py ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt \
  && rm -fr .cache
RUN python3 -m pip install -e .

COPY . /app

ARG GIT_HASH
ENV GIT_HASH=$GIT_HASH

RUN flake8 --max-line-length=120 --ignore=E702,W504 *.py tests c2corg_images \
 && scripts/check_typing.sh \
 && c2cwsgiutils-genversion $GIT_HASH \
 && mv docker-entrypoint.* /

EXPOSE 8080
ENTRYPOINT ["/docker-entrypoint.sh"]

ENV C2CORG_IMAGES_LOG_LEVEL=INFO \
    C2CWSGI_LOG_LEVEL=INFO \
    TEMP_FOLDER=/tmp/temp \
    INCOMING_FOLDER=/tmp/incoming \
    ACTIVE_FOLDER=/tmp/active \
    GUNICORN_PARAMS="-b :8080 --worker-class gthread --threads 10 --workers 5"

CMD ["c2cwsgiutils-run"]
