import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    DISCOGS_USERNAME = os.getenv('DISCOGS_USERNAME')
    CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '30'))
    
    @classmethod
    def validate(cls):
        missing = []
        
        if not cls.DISCOGS_TOKEN:
            missing.append('DISCOGS_TOKEN')
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append('TELEGRAM_BOT_TOKEN')
        if not cls.DISCOGS_USERNAME:
            missing.append('DISCOGS_USERNAME')
        
        if missing:
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            logger.error("Please create a .env file with the required variables.")
            logger.error("See .env.example for reference.")
            raise ValueError(error_msg)
        
        logger.info("Configuration validated successfully")
        return True
