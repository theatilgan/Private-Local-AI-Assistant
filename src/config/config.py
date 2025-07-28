"""
Project configuration settings.
"""
import os
from typing import Dict, Any

class Config:
    """Application configuration."""
    
    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/database.db')
    
    # Ollama settings
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma2:latest')
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    
    # Application settings
    MAX_KEYWORDS = int(os.getenv('MAX_KEYWORDS', '5'))
    MIN_KEYWORDS = int(os.getenv('MIN_KEYWORDS', '3'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Prompt templates
    KEYWORD_EXTRACTION_PROMPT = """
    Extract {min_keywords} to {max_keywords} keywords from the following student message. 
    Write only separated by commas. Do not form sentences.

    Text: "{text}"
    """
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Returns database configuration."""
        return {
            'database_path': cls.DATABASE_PATH
        }
    
    @classmethod
    def get_ollama_config(cls) -> Dict[str, Any]:
        """Returns Ollama configuration."""
        return {
            'model': cls.OLLAMA_MODEL,
            'host': cls.OLLAMA_HOST
        } 