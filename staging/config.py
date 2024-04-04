"""
This module contains the configuration for the application.
"""

from .logger import logger

CONFIG = {}


def get_format(formatter: str) -> str:
    """
    Get the flag value
    """
    if "formatter" not in CONFIG:
        CONFIG["formatter"] = {}
    return CONFIG["formatter"].get(formatter, "")


def set_format(formatter: str, value: str):
    """
    Set the flag value
    """
    if "formatter" not in CONFIG:
        CONFIG["formatter"] = {}
    logger.debug(f"Setting formatter [{formatter}] to [{value}]")
    CONFIG["formatter"][formatter] = value


def clear():
    """
    Clear the configuration
    """
    logger.debug("Clearing the configuration")
    CONFIG.clear()
