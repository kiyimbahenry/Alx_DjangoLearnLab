#!/bin/bash

# Secure Deployment Script for LibraryProject

echo "Starting secure deployment of LibraryProject..."

# Set environment variables
export DJANGO_SETTINGS_MODULE="LibraryProject.settings"
export SECRET_KEY="your-generated-secret-key"
export DEBUG="False"

# Create necessary directories
mkdir -p /var/log/gunicorn
mkdir -p /var/run/gunicorn

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Set proper permissions
chmod 755 /path/to/your/project
chmod 644 /path/to/your/project/*.py
chmod -R 755 /path/to/your/project/staticfiles
chmod -R 755 /path/to/your/project/media

# Restart services
echo "Restarting services..."
sudo systemctl restart nginx
sudo systemctl restart gunicorn

# Verify deployment
echo "Verifying deployment..."
curl -I https://yourdomain.com

echo "Deployment completed successfully!"
