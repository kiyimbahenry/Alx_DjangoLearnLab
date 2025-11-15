#!/bin/bash

# SSL Certificate Setup Script for Django Deployment
# This script sets up Let's Encrypt SSL certificates

DOMAIN="yourdomain.com"
EMAIL="admin@yourdomain.com"

echo "Setting up SSL certificates for $DOMAIN"

# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain SSL certificate
sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --preferred-challenges http --agree-tos -m $EMAIL --non-interactive

# Create a strong Diffie-Hellman group
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# Start Nginx
sudo systemctl start nginx

# Set up automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

echo "SSL certificate setup completed for $DOMAIN"
echo "Certificate location: /etc/letsencrypt/live/$DOMAIN/"
