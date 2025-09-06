"""
Configuration settings for the Gold Price Forecasting application
"""

import os

class Config:
    """Base configuration class"""
    
    # Cache settings
    CACHE_DURATION_HOURS = int(os.getenv('CACHE_DURATION_HOURS', 1))
    
    # Forecast settings
    FORECAST_PERIOD_DAYS = int(os.getenv('FORECAST_PERIOD_DAYS', 90))
    DATA_PERIOD_YEARS = int(os.getenv('DATA_PERIOD_YEARS', 2))
    
    # API settings
    YFINANCE_SYMBOL = os.getenv('YFINANCE_SYMBOL', 'GC=F')
    
    # Exchange rates (can be updated from external API)
    USD_TO_EGP_RATE = float(os.getenv('USD_TO_EGP_RATE', 48.5))
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CACHE_DURATION_HOURS = 0.5  # 30 minutes for faster testing

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    CACHE_DURATION_HOURS = 2  # 2 hours for production

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
