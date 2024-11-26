#!/bin/bash
set -e

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Execute the default CMD
exec "$@"
