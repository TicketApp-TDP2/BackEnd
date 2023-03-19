from app.config.constants import (
    PORT,
    DB_URL,
    DB_NAME,
    ENV_NAME
)
from app.config.logger import setup_logger

# TODO: Ver si esto es correcto
logger = setup_logger(name=__name__)


def log_config():
    logger.info("Configuration: ")
    logger.info(f"  - PORT: {PORT}")
    logger.info(f"  - DB_URL: {DB_URL}")
    logger.info(f"  - DB_NAME: {DB_NAME}")
    logger.info(f"  - ENV_NAME: {ENV_NAME}")
