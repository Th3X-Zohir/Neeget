# Neeget Platform - Deployment Guide

This guide provides step-by-step instructions for deploying the Neeget platform in different environments.

## 🚀 Quick Start (Development)

### Local Development Setup

1. **Prerequisites**
   ```bash
   # Ensure Python 3.11+ is installed
   python3.11 --version
   
   # Ensure pip is available
   pip3 --version
   ```

2. **Install Dependencies**
   ```bash
   cd Neeget
   pip3 install flask flask-wtf bcrypt
   ```

3. **Run the Application**
   ```bash
   python3.11 app.py
   ```

4. **Access the Application**
   - Open browser: `http://localhost:5000`
   - Admin login: `admin@neeget.com` / `password`

## 🌐 Production Deployment

### Option 1: Traditional Server Deployment

#### 1. Server Setup (Ubuntu/Debian)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-pip python3.11-venv nginx -y

# Create application user
sudo useradd -m -s /bin/bash neeget
sudo su - neeget
```

#### 2. Application Setup
```bash
# Clone/upload application files
cd /home/neeget
# Upload your Neeget folder here

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-wtf bcrypt gunicorn
```

#### 3. Gunicorn Configuration
```bash
# Create gunicorn config
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
```

#### 4. Systemd Service
```bash
# Create service file (as root)
sudo cat > /etc/systemd/system/neeget.service << EOF
[Unit]
Description=Neeget Flask Application
After=network.target

[Service]
User=neeget
Group=neeget
WorkingDirectory=/home/neeget/Neeget
Environment=PATH=/home/neeget/venv/bin
ExecStart=/home/neeget/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable neeget
sudo systemctl start neeget
```

#### 5. Nginx Configuration
```bash
# Create nginx config
sudo cat > /etc/nginx/sites-available/neeget << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /home/neeget/Neeget/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/neeget /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

#### 2. Create requirements.txt
```txt
Flask==2.3.3
Flask-WTF==1.1.1
bcrypt==4.0.1
gunicorn==21.2.0
```

#### 3. Build and Run
```bash
# Build image
docker build -t neeget-app .

# Run container
docker run -d -p 5000:5000 --name neeget neeget-app
```

#### 4. Docker Compose (Optional)
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment
1. **Create Procfile**
   ```
   web: gunicorn app:app
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### AWS EC2 Deployment
1. Launch EC2 instance (Ubuntu 22.04)
2. Follow "Traditional Server Deployment" steps
3. Configure security groups for HTTP/HTTPS access

#### DigitalOcean Droplet
1. Create Ubuntu droplet
2. Follow "Traditional Server Deployment" steps
3. Configure firewall for web traffic

## 🔧 Production Configuration

### 1. Environment Variables
```bash
# Create .env file
cat > .env << EOF
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
DATABASE_URL=your-database-url
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
EOF
```

### 2. Update config.py
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    JSON_DATABASE_DIR = os.environ.get('DATABASE_DIR') or 'data'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
```

### 3. Database Migration (Optional)
For production, consider migrating to PostgreSQL:

```python
# Install dependencies
pip install psycopg2-binary flask-sqlalchemy

# Update config for PostgreSQL
DATABASE_URL = 'postgresql://user:password@localhost/neeget'
```

## 🔒 Security Considerations

### 1. SSL/HTTPS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Firewall Configuration
```bash
# UFW setup
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 3. Security Headers
Add to Nginx config:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## 📊 Monitoring & Maintenance

### 1. Log Management
```bash
# Application logs
sudo journalctl -u neeget -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Backup Strategy
```bash
# Create backup script
cat > backup.sh << EOF
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backups/neeget_\$DATE.tar.gz /home/neeget/Neeget/data
find /backups -name "neeget_*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### 3. Health Monitoring
```bash
# Simple health check script
cat > health_check.sh << EOF
#!/bin/bash
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Application is healthy"
else
    echo "Application is down - restarting"
    sudo systemctl restart neeget
fi
EOF
```

## 🚀 Performance Optimization

### 1. Static File Serving
Configure Nginx to serve static files directly:
```nginx
location /static {
    alias /home/neeget/Neeget/static;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Caching (Optional)
Install Redis for session caching:
```bash
sudo apt install redis-server
pip install redis flask-session
```

### 3. Database Optimization
For JSON file storage:
- Regular cleanup of old data
- Implement data archiving
- Monitor file sizes

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission Issues**
   ```bash
   sudo chown -R neeget:neeget /home/neeget/Neeget
   sudo chmod -R 755 /home/neeget/Neeget
   ```

3. **Service Won't Start**
   ```bash
   sudo systemctl status neeget
   sudo journalctl -u neeget -n 50
   ```

### Performance Issues
- Check system resources: `htop`
- Monitor application logs
- Verify database file permissions
- Check network connectivity

## 📞 Support

For deployment support:
- Check application logs first
- Verify all dependencies are installed
- Ensure proper file permissions
- Test network connectivity

---

**Note**: This deployment guide covers basic production setup. For high-traffic applications, consider additional optimizations like load balancing, database clustering, and CDN integration.

