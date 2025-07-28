"""
AI services class.
"""
import logging
from typing import List, Optional
import ollama
from ..config.config import Config

logger = logging.getLogger(__name__)

class AIService:
    """Class that manages AI operations."""
    
    def __init__(self, model: str = None, host: str = None):
        """
        Initializes AIService.
        
        Args:
            model: AI model to use
            host: Ollama host address
        """
        self.model = model or Config.OLLAMA_MODEL
        self.host = host or Config.OLLAMA_HOST
        self._setup_ollama()
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Sets up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT
        )
    
    def _setup_ollama(self) -> None:
        """Sets up Ollama configuration."""
        try:
            # Configure Ollama client (set_host method doesn't exist, default host is used)
            logger.info(f"Ollama host: {self.host} (default)")
        except Exception as e:
            logger.error(f"Ollama configuration error: {e}")
            raise
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extracts keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List[str]: List of extracted keywords
            
        Raises:
            Exception: When AI service error occurs
        """
        if not text or not text.strip():
            logger.warning("Cannot extract keywords from empty text")
            return []
        
        try:
            prompt = Config.KEYWORD_EXTRACTION_PROMPT.format(
                text=text,
                min_keywords=Config.MIN_KEYWORDS,
                max_keywords=Config.MAX_KEYWORDS
            )
            
            logger.debug(f"Sending request to AI model: {self.model}")
            
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not response or 'message' not in response:
                logger.error("Invalid response received from AI service")
                return []
            
            keywords_text = response['message']['content'].strip()
            logger.info(f"Keywords received from AI: {keywords_text}")
            
            # Clean and split keywords
            keywords = [
                kw.strip() 
                for kw in keywords_text.split(',') 
                if kw.strip()
            ]
            
            # Check keyword count
            if len(keywords) < Config.MIN_KEYWORDS:
                logger.warning(f"Too few keywords extracted: {len(keywords)}")
            elif len(keywords) > Config.MAX_KEYWORDS:
                keywords = keywords[:Config.MAX_KEYWORDS]
                logger.info(f"Keywords limited to {Config.MAX_KEYWORDS}")
            
            logger.info(f"Total {len(keywords)} keywords extracted")
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            # Fallback in case of error
            return self._fallback_keyword_extraction(text)
    
    def _fallback_keyword_extraction(self, text: str) -> List[str]:
        """
        Simple keyword extraction to use when AI service is not working.
        
        Args:
            text: Text
            
        Returns:
            List[str]: Simple keywords
        """
        logger.info("Using fallback keyword extraction")
        
        # Simple word extraction (remove English stop words)
        stop_words = {
            'and', 'or', 'with', 'for', 'this', 'a', 'an', 'the', 'is', 'are',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'how', 'where',
            'which', 'who', 'why', 'because', 'but', 'however', 'although',
            'want', 'need', 'make', 'do', 'get', 'have', 'give', 'take'
        }
        
        words = text.lower().split()
        keywords = [
            word.strip('.,!?;:()[]{}"\'-') 
            for word in words 
            if word.strip('.,!?;:()[]{}"\'-') and 
               word.strip('.,!?;:()[]{}"\'-') not in stop_words and
               len(word.strip('.,!?;:()[]{}"\'-')) > 2
        ]
        
        # Get most frequent words
        from collections import Counter
        word_counts = Counter(keywords)
        top_keywords = [word for word, count in word_counts.most_common(Config.MAX_KEYWORDS)]
        
        logger.info(f"Extracted {len(top_keywords)} keywords with fallback method")
        return top_keywords
    
    def test_connection(self) -> bool:
        """
        Tests AI service connection.
        
        Returns:
            bool: Whether connection is successful
        """
        try:
            test_prompt = "Hello, this is a test message."
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": test_prompt}]
            )
            
            if response and 'message' in response:
                logger.info("AI service connection successful")
                return True
            else:
                logger.error("AI service test response invalid")
                return False
                
        except Exception as e:
            logger.error(f"AI service connection test failed: {e}")
            return False 