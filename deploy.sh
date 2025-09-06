#!/bin/bash

# Gold Price Forecasting App Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "🚀 Gold Price Forecasting App Deployment Script"
echo "================================================"

# Function to deploy to Heroku
deploy_heroku() {
    echo "📦 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install it first:"
        echo "   https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Login to Heroku
    heroku login
    
    # Create Heroku app (if it doesn't exist)
    read -p "Enter your Heroku app name (or press Enter to create new): " app_name
    if [ -z "$app_name" ]; then
        app_name="gold-forecast-$(date +%s)"
        heroku create $app_name
    fi
    
    # Set environment variables
    heroku config:set FLASK_ENV=production -a $app_name
    heroku config:set DEBUG=False -a $app_name
    heroku config:set CACHE_DURATION_HOURS=2 -a $app_name
    heroku config:set LOG_LEVEL=INFO -a $app_name
    
    # Deploy
    git add .
    git commit -m "Deploy to Heroku"
    git push heroku main
    
    echo "✅ Deployed to Heroku: https://$app_name.herokuapp.com"
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    # Build Docker image
    docker build -t gold-forecast .
    
    # Run container
    docker run -d \
        --name gold-forecast-app \
        -p 5000:5000 \
        --env-file production.env \
        --restart unless-stopped \
        gold-forecast
    
    echo "✅ Docker container running on http://localhost:5000"
    echo "📊 Health check: http://localhost:5000/health"
}

# Function to deploy to VPS/Server
deploy_vps() {
    echo "🖥️  VPS Deployment Instructions..."
    echo ""
    echo "1. Upload your code to the server"
    echo "2. Install Python 3.9+ and pip"
    echo "3. Create virtual environment:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "4. Install dependencies:"
    echo "   pip install -r requirements.txt"
    echo "5. Set environment variables:"
    echo "   export FLASK_ENV=production"
    echo "   export DEBUG=False"
    echo "6. Run with Gunicorn:"
    echo "   pip install gunicorn"
    echo "   gunicorn -w 4 -b 0.0.0.0:5000 app:app"
    echo "7. Set up reverse proxy with Nginx (optional)"
    echo "8. Set up SSL certificate (optional)"
}

# Main menu
echo "Select deployment option:"
echo "1) Heroku"
echo "2) Docker"
echo "3) VPS/Server Instructions"
echo "4) All options"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        deploy_heroku
        ;;
    2)
        deploy_docker
        ;;
    3)
        deploy_vps
        ;;
    4)
        echo "📋 All deployment options:"
        echo ""
        deploy_heroku
        echo ""
        deploy_docker
        echo ""
        deploy_vps
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process completed!"
echo "📚 For more details, check the README.md file"
