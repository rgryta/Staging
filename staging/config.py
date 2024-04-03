"""
This module contains the configuration for the application.
"""

import logging

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
    logging.info(f"Setting formatter [{formatter}] to [{value}]")
    CONFIG["formatter"][formatter] = value


def clear():
    """
    Clear the configuration
    """
    logging.info("Clearing the configuration")
    CONFIG.clear()
