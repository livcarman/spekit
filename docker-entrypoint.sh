#!/bin/sh

# Run database migrations
/venv/bin/python manage.py migrate --no-input

# Collect staticfiles
/venv/bin/python manage.py collectstatic --no-input

# Create a superuser account (if one doesn't already exist)
/venv/bin/python manage.py ensure_superuser \
    --username="$SUPERUSER_NAME" \
    --email="$SUPERUSER_EMAIL" \
    --password="$SUPERUSER_PASSWORD"

# Run uWSGI
/venv/bin/uwsgi --http-auto-chunked --http-keepalive
