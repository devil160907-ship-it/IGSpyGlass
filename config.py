import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Secure secret key generation
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/igspyglass'
    
    # Instagram API Configuration
    INSTAGRAM_API_BASE = 'https://www.instagram.com'
    
    # Essential headers for Instagram API
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
    X_IG_APP_ID = '936619743392459'  # Instagram Web App ID
    
    # Rate limiting settings
    REQUEST_DELAY = 1  # seconds between requests
    MAX_RETRIES = 3
    
    # Download settings
    DOWNLOAD_FOLDER = 'static/downloads'
    MAX_CONTENT_SIZE = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4', 'mov'}
    
    # Cache settings
    CACHE_DURATION = 3600  # 1 hour


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
