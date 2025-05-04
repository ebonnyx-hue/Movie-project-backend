import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class HostConfig:
    # Base configuration
    BASE_DIR = Path(__file__).resolve().parent
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # API settings
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
    TMDB_API_BASE_URL = 'https://api.themoviedb.org/3'
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./movies.db')
    
    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per minute')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_config(cls):
        """Returns a dictionary of all configuration settings"""
        return {
            'DEBUG': cls.DEBUG,
            'HOST': cls.HOST,
            'PORT': cls.PORT,
            'ALLOWED_ORIGINS': cls.ALLOWED_ORIGINS,
            'CACHE_TYPE': cls.CACHE_TYPE,
            'CACHE_DEFAULT_TIMEOUT': cls.CACHE_DEFAULT_TIMEOUT,
            'LOG_LEVEL': cls.LOG_LEVEL
        }

# Create an instance of the config
host_config = HostConfig() 