# Configuration for TuXun Agent  
import os  
from typing import Optional  
  
class Config:  
    # API Keys and External Services  
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv('GOOGLE_MAPS_API_KEY')  
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')  
  
    # Database settings  
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///geolocation.db')  
    VECTOR_DB_PATH: str = os.getenv('VECTOR_DB_PATH', './data/vector_db')  
  
    # Model settings  
    DEFAULT_MODEL: str = os.getenv('DEFAULT_MODEL', 'gpt-4o')  
    CONFIDENCE_THRESHOLD: float = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))  
  
    # Processing settings  
    MAX_IMAGE_SIZE: int = int(os.getenv('MAX_IMAGE_SIZE', '5000000'))  # 5MB  
    ALLOWED_IMAGE_FORMATS: list = ['JPEG', 'PNG', 'JPG', 'TIFF']  
  
    # Agent settings  
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))  
    TIMEOUT: int = int(os.getenv('TIMEOUT', '30'))  
  
    # Paths  
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', './uploads')  
    DATA_FOLDER: str = os.getenv('DATA_FOLDER', './data') 
