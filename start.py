#!/usr/bin/env python3
"""
Startup script for Gold Price Forecasting App
This script handles initialization and startup gracefully
"""

import os
import sys
import time
import logging
from app import app, fetch_and_train_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_app():
    """Initialize the application with proper error handling"""
    try:
        logger.info("Starting Gold Price Forecasting App...")
        
        # Create necessary directories
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        
        logger.info("Directories created successfully")
        
        # Initialize the model (this might take some time)
        logger.info("Initializing forecasting model...")
        fetch_and_train_model()
        logger.info("Model initialized successfully")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize app: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("=" * 50)
    logger.info("Gold Price Forecasting App Startup")
    logger.info("=" * 50)
    
    # Initialize the app
    if not initialize_app():
        logger.error("Failed to initialize app. Exiting...")
        sys.exit(1)
    
    # Get configuration
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting server on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("App is ready to serve requests!")
    
    # Start the Flask app
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
