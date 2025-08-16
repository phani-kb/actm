"""Utility functions for the ACTM project."""

import os
from typing import Any, Dict, Optional

from actm.common import constants
from actm.common.config_reader import logger


def create_folder(folder):
    """Creates a folder if it does not exist.

    :param folder: Path to the folder to be created.
    """
    is_folder_exists = os.path.exists(folder)
    if not is_folder_exists:
        os.makedirs(folder)


def write_output(output, filename=None, folder=None):
    """Writes the output to a file with the given filename in the given folder, line by line.

    :param output: List of lines to be written to the file.
    :param filename: Name of the file to write the output.
    :param folder: Folder where the file will be written (default is None).
    """
    if not filename:
        for line in output:
            print(line)
        return
    if folder:
        create_folder(folder)
    file_path = os.path.join(folder, filename) if folder else filename
    with open(file_path, "w", encoding="utf-8") as file:
        for line in output:
            file.write(f"{line}\n")


def is_contains(label, params):
    """Check if the label contains any of the parameters.

    :param label: The label to check.
    :param params: List of parameters to check.
    :return: True if the label contains any of the parameters, False otherwise.
    """
    return any(param in label for param in params)


def get_user_agent(app_config: Optional[Dict[str, Any]]) -> str:
    """Returns a user agent string with app information.
    :param app_config: Application configuration dictionary.
    :return: User agent string.
    """
    if app_config is None:
        app_config = {}
    app_name = app_config.get("name", constants.APP_NAME)
    app_ver = app_config.get("version", constants.APP_VERSION)
    app_desc = app_config.get("description", constants.APP_DESCRIPTION)
    logger.debug("App Name: %s, App Version: %s, App Description: %s", app_name, app_ver, app_desc)
    user_agent = f"{app_name}/{app_ver} ({app_desc})"
    logger.debug("User Agent: %s", user_agent)
    return user_agent
