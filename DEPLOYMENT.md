# Deployment Guide - Gold Price Forecasting Application

This guide provides step-by-step instructions for deploying your gold price forecasting application to various platforms.

## 🚀 Quick Start

### Option 1: Heroku (Easiest)
```bash
# Install Heroku CLI first: https://devcenter.heroku.com/articles/heroku-cli
heroku login
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Option 2: Docker
```bash
docker build -t gold-forecast .
docker run -p 5000:5000 gold-forecast
```

### Option 3: VPS/Server
```bash
# On your server
git clone <your-repo>
cd gold_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn -c gunicorn.conf.py app:app
```

## 📋 Prerequisites

- Python 3.9 or higher
- Git
- Internet connection
- Domain name (optional, for custom domain)

## 🌐 Deployment Options

### 1. Heroku Deployment

**Pros:** Easy, free tier available, automatic deployments
**Cons:** Limited resources on free tier, sleeps after inactivity

#### Steps:
1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-gold-forecast-app
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set DEBUG=False
   heroku config:set CACHE_DURATION_HOURS=2
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Open Your App**
   ```bash
   heroku open
   ```

### 2. Docker Deployment

**Pros:** Consistent environment, easy scaling, portable
**Cons:** Requires Docker knowledge

#### Steps:
1. **Build Docker Image**
   ```bash
   docker build -t gold-forecast .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name gold-forecast-app \
     -p 5000:5000 \
     --env-file production.env \
     --restart unless-stopped \
     gold-forecast
   ```

3. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Check Status**
   ```bash
   docker ps
   curl http://localhost:5000/health
   ```

### 3. VPS/Server Deployment

**Pros:** Full control, better performance, custom domain
**Cons:** Requires server management knowledge

#### Steps:
1. **Prepare Server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3.9 python3.9-venv python3-pip nginx -y
   ```

2. **Deploy Application**
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd gold_project
   
   # Create virtual environment
   python3.9 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Gunicorn**
   ```bash
   # Install Gunicorn
   pip install gunicorn
   
   # Create systemd service
   sudo nano /etc/systemd/system/gold-forecast.service
   ```

   **Service file content:**
   ```ini
   [Unit]
   Description=Gold Price Forecasting App
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/your/gold_project
   Environment="PATH=/path/to/your/gold_project/venv/bin"
   ExecStart=/path/to/your/gold_project/venv/bin/gunicorn -c gunicorn.conf.py app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start gold-forecast
   sudo systemctl enable gold-forecast
   ```

5. **Configure Nginx (Optional)**
   ```bash
   sudo nano /etc/nginx/sites-available/gold-forecast
   ```

   **Nginx configuration:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/gold-forecast /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### 4. AWS Deployment

**Pros:** Scalable, reliable, many services
**Cons:** Complex, can be expensive

#### Using AWS Elastic Beanstalk:
1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   eb init
   eb create production
   ```

3. **Deploy**
   ```bash
   eb deploy
   ```

#### Using AWS EC2:
Follow VPS deployment steps, but on an EC2 instance.

### 5. Google Cloud Platform

**Pros:** Good free tier, easy integration
**Cons:** Learning curve

#### Using App Engine:
1. **Install Google Cloud SDK**
2. **Create app.yaml**
   ```yaml
   runtime: python39
   instance_class: F1
   
   env_variables:
     FLASK_ENV: production
     DEBUG: False
   ```

3. **Deploy**
   ```bash
   gcloud app deploy
   ```

## 🔧 Environment Configuration

### Production Environment Variables
```bash
FLASK_ENV=production
DEBUG=False
PORT=5000
CACHE_DURATION_HOURS=2
FORECAST_PERIOD_DAYS=90
DATA_PERIOD_YEARS=2
YFINANCE_SYMBOL=GC=F
USD_TO_EGP_RATE=48.5
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key
```

## 🔍 Monitoring & Maintenance

### Health Checks
Your app includes a health check endpoint:
```bash
curl https://your-app.com/health
```

### Logs
- **Heroku:** `heroku logs --tail`
- **Docker:** `docker logs gold-forecast-app`
- **VPS:** `sudo journalctl -u gold-forecast -f`

### Updates
```bash
# Pull latest changes
git pull origin main

# Restart service (VPS)
sudo systemctl restart gold-forecast

# Rebuild Docker
docker-compose down
docker-compose up -d --build
```

## 🛡️ Security Considerations

1. **Change default secret key**
2. **Use HTTPS in production**
3. **Set up firewall rules**
4. **Regular security updates**
5. **Monitor logs for suspicious activity**

## 📊 Performance Optimization

1. **Enable caching** (already implemented)
2. **Use CDN for static files**
3. **Database optimization** (if adding database)
4. **Load balancing** (for high traffic)

## 🆘 Troubleshooting

### Common Issues:

1. **Port already in use**
   ```bash
   # Find process using port
   lsof -i :5000
   # Kill process
   kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   chmod +x deploy.sh
   sudo chown -R www-data:www-data /path/to/app
   ```

3. **Module not found**
   ```bash
   pip install -r requirements.txt
   ```

4. **Memory issues**
   - Reduce `FORECAST_PERIOD_DAYS`
   - Increase server memory
   - Use caching more aggressively

## 📞 Support

If you encounter issues:
1. Check the logs
2. Verify environment variables
3. Test locally first
4. Check the health endpoint
5. Review this documentation

## 🎯 Next Steps

After successful deployment:
1. Set up monitoring (UptimeRobot, Pingdom)
2. Configure custom domain
3. Set up SSL certificate
4. Implement backup strategy
5. Set up automated deployments
