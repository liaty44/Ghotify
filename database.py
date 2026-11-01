from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
import logging

logger = logging.getLogger("GHOTIFY")

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = AsyncIOMotorClient(Config.MONGO_URI)
            self.db = self.client.get_default_database()
            logger.info("MongoDB connected successfully for GHOTIFY.")
        except Exception as e:
            logger.critical(f"Database connection failed: {e}")

db = Database()
