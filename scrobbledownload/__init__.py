"""
Some initialization functinos for the application
"""
import logging
import sys


def initialize_logger(log_level: int = logging.INFO):
    """
    Initialize the logger for the application. We sendeverything through stderr since this is designed for Docker.
    Args:
        log_level (str): The log level to initialize with
    """
    logger = logging.getLogger("scrobbledownload")
    logger.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)
