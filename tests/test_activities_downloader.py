from unittest.mock import patch
from actm.downloaders.activities_downloader import ActivitiesDownloader
from actm.common.enums import DownloadType


class DummyDriver:
    def __init__(self):
        self.page_source = "<html></html>"

    def get(self, url):
        pass

    def save_screenshot(self, path):
        with open(path, "w") as f:
            f.write("screenshot")

    def quit(self):
        pass


def test_activities_downloader_init(tmp_path):
    driver = DummyDriver()
    output_folder = tmp_path
    with patch("selenium.webdriver.Chrome"):
        downloader = ActivitiesDownloader(driver, str(output_folder))
    assert downloader.output_folder == str(output_folder)
    assert downloader.dtype == DownloadType.ACTIVITIES


def test_activities_downloader_min_max_age(tmp_path):
    driver = DummyDriver()
    with patch("selenium.webdriver.Chrome"):
        downloader = ActivitiesDownloader(driver, str(tmp_path))
    downloader.min_age = 5
    downloader.max_age = 15
    assert downloader.min_age == 5
    assert downloader.max_age == 15
