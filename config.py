"""
Configuration settings for the Travel Planner application.
Supports different environments (development, production, testing).
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://localhost/travel_planner'
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Application settings
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    DATABASE_URL = os.environ.get('DEV_DATABASE_URL') or 'postgresql://localhost/travel_planner_dev'


class ProductionConfig(Config):
    """Production environment configuration."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable must be set in production")


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DATABASE_URL = os.environ.get('TEST_DATABASE_URL') or 'postgresql://localhost/travel_planner_test'


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name=None):
    """Get configuration class based on environment name."""
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_map.get(env_name, DevelopmentConfig)