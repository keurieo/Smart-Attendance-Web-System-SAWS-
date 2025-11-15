# SSL/TLS Certificate Setup

This directory should contain your SSL/TLS certificates for HTTPS support.

## Development (Self-Signed Certificate)

For local development, you can generate a self-signed certificate:

```bash
# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

**Note:** Self-signed certificates will show security warnings in browsers. This is normal for development.

## Production

For production, use certificates from a trusted Certificate Authority (CA):

### Option 1: Let's Encrypt (Free)

Use Certbot to obtain free SSL certificates:

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot

# Obtain certificate (replace with your domain)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to this directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### Option 2: Commercial CA

If you purchased a certificate from a commercial CA:

1. Place the certificate file as `cert.pem`
2. Place the private key file as `key.pem`
3. Ensure proper file permissions (readable only by nginx)

## File Permissions

Ensure proper permissions for security:

```bash
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem
```

## Certificate Renewal

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab for automatic renewal
sudo crontab -e
# Add this line:
0 0 * * * certbot renew --quiet && docker-compose restart nginx
```

## Verification

Test your SSL configuration:

```bash
# Check certificate details
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:443 -servername localhost
```

## Security Best Practices

1. **Never commit private keys to version control**
2. Use strong key sizes (minimum 2048-bit RSA or 256-bit ECC)
3. Keep certificates up to date
4. Use TLS 1.2 or higher only
5. Enable HSTS headers (already configured in nginx.prod.conf)
6. Test your configuration with SSL Labs: https://www.ssllabs.com/ssltest/

## Troubleshooting

### Certificate not found error

Ensure the certificate files exist and have correct names:
- `nginx/ssl/cert.pem` (certificate)
- `nginx/ssl/key.pem` (private key)

### Permission denied error

Check file permissions and ownership:
```bash
ls -la nginx/ssl/
```

### Certificate expired

Renew your certificate and restart nginx:
```bash
sudo certbot renew
docker-compose restart nginx
```
