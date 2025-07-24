"""This module contains the ConfigReader class that reads the configuration file"""

import logging

logger = logging.getLogger("actm")


class ACTMConfig:
    """Class to hold the ACTM configuration settings."""

    def __init__(self, data):
        self.log_config_file = data.get("log_config_file", "logging.yml")
