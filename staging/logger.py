"""
Staging logger
"""

import logging

logger = logging.getLogger("staging")


def setup_logger(level: int = logging.WARNING):
    """
    Setup the logger
    """
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(handler)

    logger.setLevel(level)
