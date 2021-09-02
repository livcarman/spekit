# Dockerfile boilerplate taken from my Gist:
# https://gist.github.com/livcarman/44c94f657114371b137b7ab38333ed79

# Depends on the $PORT environment variable (for compatibility with Heroku)
FROM python:3.9.7-alpine3.14

# Send output from Python directly to the container log
ENV PYTHONBUFFERED=1

# Set a working directory
WORKDIR /usr/src/app/

# Copy requirements file to known location
COPY requirements.txt /requirements.txt

# Install build deps, run `pip install`, and remove unneeded build deps all
# in a single step. This keeps the final image size small.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            git \
            jpeg-dev \
            libc-dev \
            libffi-dev \
            linux-headers \
            make \
            musl-dev \
            openssh \
            pcre-dev \
            postgresql-dev \
            zlib-dev \
    && python3.9 -m venv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Install run deps
RUN apk add --no-cache expat postgresql-client

# Copy application code to the container
COPY . /usr/src/app

# uWSGI configuration.
# ENV USGI_DIE_ON_TERM=true is required for some cloud providers like Heroku
# https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html
ENV UWSGI_VIRTUALENV=/venv
ENV UWSGI_WSGI_FILE=spekit/wsgi.py
ENV UWSGI_HTTP_SOCKET=:$(PORT)
ENV UWSGI_DIE_ON_TERM=true
ENV UWSGI_MASTER=1
ENV UWSGI_WORKERS=16
ENV UWSGI_UID=1000
ENV UWSGI_GID=2000
ENV UWSGI_LAZY_APPS=1
ENV UWSGI_WSGI_ENV_BEHAVIOR=holy

# This script runs a number of administrative tasks that need to be performed
# before the app can start, like running database migrations. It's also
# responsible for starting uWSGI.
RUN ["chmod", "+x", "/usr/src/app/docker-entrypoint.sh"]
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
