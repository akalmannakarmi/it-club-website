#!/bin/sh
set -e

echo "Running collect static"
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running add groups"
python manage.py add_groups

echo "Starting server..."
exec "$@"
