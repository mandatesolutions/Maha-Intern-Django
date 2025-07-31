#!/bin/bash

# Exit immediately if a command fails
set -e

# shellcheck disable=SC2162
read -p "Enter commit message: " msg

echo "🔄 Cleaning up existing migrations and cache..."

# Delete all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -r {} +

echo "✅ Migrations and cache cleaned."

echo "📦 Running makemigrations and migrate..."
python manage.py makemigrations
python manage.py migrate --fake-initial

echo "📁 (Optional) Collecting static files..."
python manage.py collectstatic --noinput

echo "📂 Cleaning up old .pyc files..."
find . -name "*.pyc" -delete

echo "🗂️ Staging files for commit..."
git add .

echo "📝 Committing..."
git commit -m "$msg"

echo "⬆️ Pushing to GitHub..."
git push origin main

echo "✅ Deploy script completed. GitHub Actions will handle server deployment."
