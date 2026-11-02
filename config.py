import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_NAME = "GHOTIFY"
    PREFIX = os.getenv("PREFIX", "-")
    TOKEN = os.getenv("BOT_TOKEN", "")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ghotify")
    
    # Embed Colors
    COLOR_PRIMARY = 0x3498db
    COLOR_SUCCESS = 0x2ecc71
    COLOR_ERROR = 0xe74c3c
    COLOR_WARNING = 0xf1c40f

    # Features Configuration
    ENABLE_AUTOMOD = True
    ENABLE_LEVELING = True
  
