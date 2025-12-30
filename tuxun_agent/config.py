# Configuration for TuXun Agent
import os
from typing import Optional

class Config:
    # API Keys and External Services
    SILICON_FLOW_API_KEY: Optional[str] = os.getenv('SILICON_FLOW_API_KEY')
    SILICON_FLOW_BASE_URL: str = os.getenv('SILICON_FLOW_BASE_URL', 'https://api.siliconflow.com/v1')
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv('GOOGLE_MAPS_API_KEY')
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')

    # Model settings
    DEFAULT_MODEL: str = os.getenv('DEFAULT_MODEL', 'qwen2.5-72b-instruct')
    MODEL_TEMPERATURE: float = float(os.getenv('MODEL_TEMPERATURE', '0.3'))
    CONFIDENCE_THRESHOLD: float = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))

    # Database settings
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///geolocation.db')
    VECTOR_DB_PATH: str = os.getenv('VECTOR_DB_PATH', './data/vector_db')

    # Processing settings
    MAX_IMAGE_SIZE: int = int(os.getenv('MAX_IMAGE_SIZE', '5000000'))  # 5MB
    ALLOWED_IMAGE_FORMATS: list = os.getenv('ALLOWED_IMAGE_FORMATS', 'JPEG,PNG,JPG,TIFF').split(',')

    # Agent settings
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    TIMEOUT: int = int(os.getenv('TIMEOUT', '30'))

    # Paths
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', './uploads')
    DATA_FOLDER: str = os.getenv('DATA_FOLDER', './data')

    # API Server settings
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
