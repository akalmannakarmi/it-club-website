#!/bin/sh
set -e

DEBUG_VALUE=$(echo "${DEBUG:-false}" | tr '[:upper:]' '[:lower:]')

if [ "$DEBUG_VALUE" != "true" ]; then
    echo "Running collect static"
    python manage.py collectstatic --noinput
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running add groups"
python manage.py add_groups

echo "Starting server..."
if [ "$DEBUG_VALUE" = "true" ]; then
    echo "DEBUG=true → Running Django development server"
    python manage.py runserver 0.0.0.0:8000
else
    echo "DEBUG!=true → Running Gunicorn"
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
fi
