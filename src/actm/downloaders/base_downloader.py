"""Base class for web downloaders."""

import os
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from actm.common.config_reader import logger
from actm.common.constants import ALL_AGES_MAX, ALL_AGES_MIN
from actm.common.enums import DataSaveFormat, DownloadType


class IWebDownloader(ABC):
    """Interface for web downloaders."""

    @abstractmethod
    def pre_process(self):
        """Pre-process the data before downloading."""

    @abstractmethod
    def post_process(self):
        """Post-process the data after downloading."""

    @abstractmethod
    def download_activities(self, url: str, save_format: DataSaveFormat, filters: dict):
        """Download activities from the website."""

    @abstractmethod
    def get_file_name(self, save_format: DataSaveFormat) -> str:
        """Get the file name for the downloaded data."""

    @abstractmethod
    def save_data(self, data: list[dict], save_format: DataSaveFormat):
        """Save the downloaded data to a file."""

    @abstractmethod
    def download(
        self,
        download_type: DownloadType,
        home_url: str,
        data_save_format: DataSaveFormat,
        filters: dict,
    ):
        """Download the data based on the download type."""

    @abstractmethod
    def downloaded_file_exists(self, data_save_format: DataSaveFormat) -> bool:
        """Check if the downloaded file exists."""

    @abstractmethod
    def extract_data(self, data_save_format: DataSaveFormat, filters: dict) -> None:
        """Extract data from the downloaded file based on the filters."""


def save_page_source(page, file_path, beautify=False):
    """Save the page source to a file."""

    if beautify:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(page, "html.parser")
        page = soup.prettify()

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(page)
    logger.info("Page source saved to file: %s", file_path)


def parse_age_range(age_range: str):
    """Parse the age range string and return the from and to ages."""
    import re

    match = re.search(r"Age at least (\d+) yrs but less than (\d+) yrs", age_range)
    if match:
        age_from = int(match.group(1).strip())
        age_to = int(match.group(2).strip())
        return age_from, age_to
    match = re.search(r"(\d+) yrs +", age_range)
    if match:
        age_from = int(match.group(1).strip())
        return age_from, None
    if "All ages" in age_range:
        return ALL_AGES_MIN, ALL_AGES_MAX

    return None, None


def _save_to_file(data, file_path, save_format: DataSaveFormat):
    """Helper method to save data to a file."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            if save_format == DataSaveFormat.JSON:
                import json  # pylint: disable=import-outside-toplevel

                json.dump(data, file, ensure_ascii=False, indent=2)
            elif save_format == DataSaveFormat.CSV:
                import csv  # pylint: disable=import-outside-toplevel

                writer = csv.writer(file)
                if data:
                    headers = data[0].keys()
                    writer.writerow(headers)
                    for row in data:
                        writer.writerow(row.values())
                else:
                    logger.warning("No data to save to CSV: %s", file_path)
            else:
                file.write("\n".join(data))
        logger.info("Data saved to file: %s", file_path)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error saving data: %s", e)


class BaseDownloader(IWebDownloader, ABC):
    """Base class for web downloaders."""

    def __init__(self, driver, output_folder, dtype: DownloadType, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("start-maximized")
        self.driver_service = Service(driver)
        self.driver = webdriver.Chrome(service=self.driver_service, options=chrome_options)
        self.output_folder = output_folder
        self.dtype = dtype

    def pre_process(self):
        pass

    def post_process(self):
        pass

    def download(
        self,
        download_type: DownloadType,
        home_url: str,
        data_save_format: DataSaveFormat,
        filters: dict,
    ):
        """Download the data based on the download type."""
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"  # noqa: E501
        logger.debug("User agent: %s", user_agent)
        try:
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
            if download_type == DownloadType.ACTIVITIES:
                activities_filter = filters.get("activities", {})
                self.download_activities(home_url, data_save_format, activities_filter)
            else:
                raise ValueError(f"Download type {download_type} is not supported.")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error downloading data: %s", e)
            print(e)

    def get_file_name(self, save_format: DataSaveFormat) -> str:
        """Get the file name for the downloaded data."""
        return f"{self.dtype.id}.{save_format.id}"

    def get_page_source_file_path(self):
        """Get the file path for the page source."""
        os.makedirs(self.output_folder, exist_ok=True)
        return f"{self.output_folder}/page_source.html"

    def get_skipped_file_name(self, save_format: DataSaveFormat):
        """Get the file name for the skipped activities."""
        return f"{self.dtype.id}_skipped.{save_format.id}"

    def save_data(self, data, save_format: DataSaveFormat):
        """Save the downloaded data to a file."""
        file_name = self.get_file_name(save_format)
        file_path = os.path.join(self.output_folder, file_name)
        os.makedirs(self.output_folder, exist_ok=True)
        _save_to_file(data, file_path, save_format)

    def save_skipped_data(self, skipped_activities, save_format: DataSaveFormat):
        """Save the skipped activities to a file."""
        file_name = self.get_skipped_file_name(save_format)
        file_path = os.path.join(self.output_folder, file_name)
        os.makedirs(self.output_folder, exist_ok=True)
        _save_to_file(skipped_activities, file_path, save_format)


class DownloaderFactory:
    """Factory class for creating downloader instances."""

    @staticmethod
    def get_downloader(driver, dtype: DownloadType, output_folder) -> IWebDownloader:
        """Get the appropriate downloader for the given download type."""

        if dtype == DownloadType.ACTIVITIES:
            from actm.downloaders.activities_downloader import ActivitiesDownloader

            return ActivitiesDownloader(driver, output_folder)
        return None  # type: ignore
