from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config.constants import DB_URL, DB_NAME, ENV_NAME
from app.config.logger import setup_logger
from pymongo_inmemory import MongoClient as MemoryMongoClient
from pathlib import Path
import shutil

logger = setup_logger(__name__)


def get_database():
    if ENV_NAME == 'TEST':
        conn = MemoryMongoClient()
        logger.info("Memory DB initialized")
        return conn[DB_NAME]
    else:
        while True:
            try:
                conn = MongoClient(DB_URL, serverSelectionTimeoutMS=5000)
                conn.admin.command('ismaster')
                logger.info("Connection with DB established")
                return conn[DB_NAME]
            except ConnectionFailure:
                logger.error("DB not available, retrying...")


db = get_database()


def clear_db():
    # Clear MongoDB
    for name in db.list_collection_names():
        db.drop_collection(name)
