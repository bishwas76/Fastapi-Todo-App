import logging

from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
from app.core.config import LOGS_ROOT, LOG_FILE
import os


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create file handler
    if not os.path.exists(LOGS_ROOT):
        os.makedirs(LOGS_ROOT)
        
    file_handler = TimedRotatingFileHandler(
        filename=f"{LOGS_ROOT}/{LOG_FILE}",
        when="D",
        interval=1,
        backupCount=5,
    )
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter and add it to handlers
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s(%(name)s.%(lineno)s) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()