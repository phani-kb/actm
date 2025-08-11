"""This module contains the ConfigReader class that reads the configuration file"""

import logging
import logging.config
import os
from typing import Any, Dict, Optional, Union

import yaml

from actm.common.enums import DownloadType

logger = logging.getLogger("actm")


class ACTMConfig:
    """Class to hold the ACTM configuration settings."""

    def __init__(self, data):
        self.log_config_file = data.get("log_config_file", "logging.yml")
        self.web_driver = data.get("web_driver", "chrome")
        self.input = data.get("input", {})
        self.output = data.get("output", {})
        self.output_folder = data.get("output", {}).get("folder", "output")
        self.home_url = data.get("home_url")
        self.filters = data.get("filters", {})

    def get(self, key: str) -> Union[Dict[str, Any], str]:
        """Get the value of a key in the configuration data."""
        return getattr(self, key)

    def get_input(self) -> Dict[str, Any]:
        """Get the input settings."""
        return self.input

    def get_output(self) -> Dict[str, Any]:
        """Get the output settings."""
        return self.output

    def get_filters(self) -> Dict[str, Any]:
        """Get the filters."""
        return self.filters

    def get_dtype_filters(self, dtype: DownloadType):
        """Get the DownloadType specific filters."""
        return self.filters.get(dtype.id, {})


class ConfigReader:
    """Read a configuration file."""

    def __init__(self, file_path):
        self._file_path = file_path
        config_data: Optional[Dict[str, Any]] = self._read_config()
        self._config: Optional[ACTMConfig] = ACTMConfig(config_data) if config_data else None
        self._configure_logging()

    @property
    def file_path(self) -> str:
        """Get the path to the configuration file."""
        return self._file_path

    @property
    def config(self):
        """Get the ACTM configuration settings."""
        return self._config

    def _read_config(self) -> Optional[Dict[str, Any]]:
        try:
            with open(self.file_path, encoding="utf-8") as file:
                return yaml.safe_load(file.read())
        except FileNotFoundError:
            logging.exception("Error: The file %s was not found.", self.file_path)
            return None
        except yaml.YAMLError as e:
            logging.exception("Error parsing YAML file: %s", e)
            return None

    def _configure_logging(self) -> None:
        if self.config:
            log_config_file = self.config.log_config_file
            try:
                with open(log_config_file, "r", encoding="utf-8") as file:
                    log_config = yaml.safe_load(file.read())
                    _ensure_log_directories(log_config)
                    logging.config.dictConfig(log_config)
            except FileNotFoundError:
                _setup_basic_logging()
        else:
            _setup_basic_logging()


def _ensure_log_directories(log_config: Dict[str, Any]) -> None:
    """Ensure all log directories exist."""
    handlers = log_config.get("handlers", {})
    for handler_config in handlers.values():
        if "filename" in handler_config:
            log_file = handler_config["filename"]
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)


def _setup_basic_logging() -> None:
    """Set up basic logging configuration."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            filename="logs/actm.log",
            filemode="a",
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )


def validate_config(actm_config: ACTMConfig):
    """Validate the ACTM configuration settings."""
    input_folder = actm_config.get_input().get("folder")
    output_folder = actm_config.get_output().get("folder")
    required_paths = {
        "input folder": input_folder,
        "output folder": output_folder,
    }

    for name, path in required_paths.items():
        if not isinstance(path, str) or not path:
            logger.error("%s not found in config file.", name.capitalize())
            return False
        if not os.path.exists(path):
            logger.error("%s does not exist.", name.capitalize())
            return False

    if not actm_config.home_url:
        logger.error("Home URL not found in config file.")
        return False

    filters = actm_config.get_filters()
    if not isinstance(filters, dict):
        logger.error("Filters section in config must be a dictionary.")
        return False
    age_from = filters.get("age_from")
    age_to = filters.get("age_to")
    if age_from and not isinstance(age_from, int):
        logger.error("age_from must be an integer.")
        return False
    if age_to and not isinstance(age_to, int):
        logger.error("age_to must be an integer.")
        return False

    if age_from and age_to and age_from >= age_to:
        logger.error("age_to must be greater than age_from.")
        return False

    return True
