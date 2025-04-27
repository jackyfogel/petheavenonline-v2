#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python packages
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply DB migrations
python manage.py migrate

# Load blog posts from fixture
