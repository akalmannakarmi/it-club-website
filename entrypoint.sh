#!/bin/sh
set -e

echo "Running collect static"
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"
