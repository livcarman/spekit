#!/bin/sh

# Run database migrations
/venv/bin/python manage.py migrate

# Run uWSGI
/venv/bin/uwsgi --http-auto-chunked --http-keepalive
