import logging
import os
from logging.handlers import RotatingFileHandler
from logging import DEBUG, Formatter, StreamHandler


def setup_logger(name):
    DEFAULT_FORMATTER = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s \
                        [level: %(levelname)s]"
    MAX_BYTES = 10000000
    BACKUP_COUNT = 7

    logger = logging.getLogger(name)
    scope = os.getenv(key="SCOPE", default="local")
    log_formatter = Formatter(DEFAULT_FORMATTER)
    logger.setLevel(DEBUG)

    if scope in ("local", "debug", "develop"):
        rotating_file_handler = RotatingFileHandler(
            filename="logs/app.log", maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
        )
        rotating_file_handler.setFormatter(log_formatter)
        logger.addHandler(rotating_file_handler)
    else:
        stream_handler = StreamHandler()
        stream_handler.setFormatter(log_formatter)
        logger.addHandler(stream_handler)

    return logger
