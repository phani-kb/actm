"""Scraper for activities."""

import os
import time

from bs4 import BeautifulSoup
from dateutil.parser import ParserError, parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # noqa N812
from selenium.webdriver.support.ui import WebDriverWait

from actm.common import utils
from actm.common.config_reader import logger
from actm.common.constants import (
    ALL_AGES_MAX,
    ALL_AGES_MIN,
    LOAD_WAIT_TIME,
    LOAD_WAIT_TIME1,
    LOAD_WAIT_TIME3,
    LOAD_WAIT_TIME5,
    SEARCH_WAIT_TIME,
)
from actm.common.enums import DataSaveFormat, DownloadType
from actm.scrapers.base_scraper import BaseScraper, parse_age_range, save_page_source


def should_skip_activity_date_based(date_range, filters):
    """Check if the activity should be skipped based on the date range."""
    skip_single_date = filters["when"].get("skip_single_date")
    if skip_single_date:
        try:
            start_date = parse(date_range, fuzzy=True, default=None)
            end_date = parse(date_range.split("to")[-1], fuzzy=True, default=None)
            return not (start_date and end_date and start_date != end_date)
        except ParserError:
            return False
    return False


def should_skip_activity_age_based(age_from, age_to, filters):
    """Check if the activity should be skipped based on the age range."""
    filter_age_from = filters["who"].get("age_from")
    filter_age_to = filters["who"].get("age_to")
    skip_all_ages = filters["who"].get("skip_all_ages")

    if filter_age_from is not None:
        filter_age_from = int(filter_age_from)
    if filter_age_to is not None:
        filter_age_to = int(filter_age_to)

    if age_from is not None and age_to is None:
        age_to = 100  # Treat age_to as 100 if it is None, meaning 6+ years

    if age_from is not None and age_to is not None:
        if skip_all_ages and age_from == ALL_AGES_MIN and age_to == ALL_AGES_MAX:
            return True
        if filter_age_from is not None and filter_age_from > age_to:
            return True
        if filter_age_to is not None and filter_age_to < age_from:
            return True
    elif age_from is None and age_to is not None:
        if filter_age_from is not None and filter_age_from > age_to:
            return True
    elif age_from is None and age_to is None:
        if filter_age_from is not None or filter_age_to is not None:
            return True

    return False


def extract_activities_from_page_source(file_path, filters):
    """Extract activities from the page source HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        page_source = file.read()

    soup = BeautifulSoup(page_source, "html.parser")
    activity_cards = soup.find_all("div", class_="card activity-card activity-card--no-status")

    activities = []
    skipped_activities = []
    skip_count = 0

    for card in activity_cards:
        name_elem = card.find("div", class_="activity-card-info__name-link").find("a")
        activity_name = name_elem.text.strip()
        if utils.is_contains(
            activity_name.lower(), [f.lower() for f in filters["name"]["not_contains"]]
        ):
            skip_count += 1
            skipped_activities.append({"Name": activity_name})
            continue

        activity_url = name_elem["href"].strip()
        activity_number = (
            card.find("span", class_="activity-card-info__number").find("span").text.strip()
        )
        location = (
            card.find("div", class_="activity-card-info__location").find("span").text.strip()
        )

        age_elem = card.find("span", class_="activity-card-info__ages")
        separator_elem = age_elem.find("span", class_="activity-card-info__separator")
        if separator_elem:
            separator_elem.decompose()
        age_range = age_elem.text.strip()
        age_from, age_to = parse_age_range(age_range)

        if should_skip_activity_age_based(age_from, age_to, filters):
            skip_count += 1
            skipped_activities.append({"Name": activity_name})
            continue

        try:
            date_range = (
                card.find("span", class_="activity-card-info__dateRange").find("span").text.strip()
            )
            if should_skip_activity_date_based(date_range, filters):
                skip_count += 1
                skipped_activities.append({"Name": activity_name})
                continue

        except AttributeError:
            date_range = "Couldn't find date range: Check the website"

        try:
            time_range = (
                card.find("span", class_="activity-card-info__timeRange").find("span").text.strip()
            )
        except AttributeError:
            time_range = "Couldn't find time range: Check the website"

        activities.append(
            {
                "Name": activity_name,
                "Location": location,
                "Age Range": age_range,
                "Date Range": date_range,
                "Time Range": time_range,
                "Activity Number": activity_number,
                "URL": activity_url,
            }
        )

    logger.info("Extracted %s activities", len(activities))
    logger.info("Skipped %s activities", skip_count)
    return activities, skipped_activities


class ActivitiesScraper(BaseScraper):
    """Scraper for activities."""

    def __init__(self, driver, output_folder, headless=True):
        super().__init__(driver, output_folder, DownloadType.ACTIVITIES, headless=headless)
        self.wait = WebDriverWait(self.driver, SEARCH_WAIT_TIME)
        self._min_age = 8
        self._max_age = 12

    @property
    def min_age(self):
        """Get the minimum age for the activities."""
        return self._min_age

    @min_age.setter
    def min_age(self, value):
        self._min_age = value

    @property
    def max_age(self):
        """Get the maximum age for the activities."""
        return self._max_age

    @max_age.setter
    def max_age(self, value):
        self._max_age = value

    def download_activities(self, url: str, save_format: DataSaveFormat, filters: dict):
        logger.info("Scraping activities...")
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, LOAD_WAIT_TIME)
            wait.until(EC.presence_of_element_located((By.ID, "app-root")))

            activities_menu = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Activities")))
            activities_menu.click()

            time.sleep(LOAD_WAIT_TIME)  # Give some time to load
            wait.until(EC.presence_of_element_located((By.ID, "main-content-body")))
            wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "loading-bar__outer-box"))
            )

            self.apply_when_filter(filters)
            self.apply_who_filter(filters)
            self.apply_where_filter(filters)

            # get the total number of activities to be scraped
            total_activities = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//div[@class="activity-results-header__total"]/span/b',
                    )
                )
            ).text
            logger.info("Total Activities Found: %s", total_activities)

            logger.info("Scrolling to the bottom of the page...")
            self.scroll_to_bottom()
            logger.info("Scrolled to the bottom of the page")
            time.sleep(SEARCH_WAIT_TIME)

            page_source = self.driver.page_source
            ps_file_path = self.get_page_source_file_path()
            save_page_source(page_source, ps_file_path, True)
            logger.info("Saved the page source to a file: %s", ps_file_path)

            # save the page screenshot to a file
            screenshot_file_path = f"{self.output_folder}/full_page_screenshot.png"
            self.driver.save_screenshot(screenshot_file_path)
            logger.info("Saved the full page screenshot to a file: %s", screenshot_file_path)

            activities, skipped_activities = extract_activities_from_page_source(
                ps_file_path, filters
            )
            self.save_data(activities, save_format)
            self.save_skipped_data(skipped_activities, save_format)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error scraping activities: %s", e)
        finally:
            self.driver.quit()
            logger.info("Activities scraping complete")

    def apply_when_filter(self, filters: dict):
        """Apply the 'When' filter based on the provided filters."""
        if "when" not in filters:
            return

        if "session_checkboxes" not in filters["when"]:
            return

        if not len(filters["when"]["session_checkboxes"]) > 0:
            return

        wait = WebDriverWait(self.driver, LOAD_WAIT_TIME)
        when_filter = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Filter When selected"]'))
        )
        when_filter.click()
        logger.info("Clicked When filter")
        time.sleep(LOAD_WAIT_TIME5)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "an-focus-trap")))
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "filter-sections")))

        view_more_element = WebDriverWait(self.driver, LOAD_WAIT_TIME).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listbox__show-more-link"))
        )
        view_more_element.click()
        logger.info("Clicked View more element")
        time.sleep(LOAD_WAIT_TIME5)

        session_checkboxes = WebDriverWait(self.driver, LOAD_WAIT_TIME).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//div[@class='filter-sections filter-sections-checkbox']/fieldset/legend[text()='Session']/../div[@class='checkbox-group']//input[@type='checkbox']",  # noqa: E501
                )
            )
        )
        time.sleep(LOAD_WAIT_TIME)

        for checkbox in session_checkboxes:
            label = checkbox.find_element(
                By.XPATH, "./following-sibling::span[@class='checkbox__text']/span"
            ).text
            if utils.is_contains(label, filters["when"]["session_checkboxes"]):
                checkbox.click()
                print(f"Clicked checkbox: {label}")
                time.sleep(LOAD_WAIT_TIME1)

        logger.info("Clicked Session checkboxes")

        if "status" in filters["when"] and len(filters["when"]["status"]) > 0:
            radio_buttons = WebDriverWait(self.driver, LOAD_WAIT_TIME).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//div[@class='filter-sections filter-sections-radio activity-filter-popper__status-section']/fieldset/legend[text()='Status']/../div[@class='radio-group']//span/input[@type='radio']",  # noqa: E501
                    )
                )
            )
            time.sleep(LOAD_WAIT_TIME)

            for radio in radio_buttons:
                label = radio.find_element(By.XPATH, "./following-sibling::span/span").text
                if label.lower() == filters["when"]["status"].lower():
                    radio.click()
                    print(f"Clicked radio button: {label}")
                    time.sleep(LOAD_WAIT_TIME1)
            logger.info("Clicked Status radio button")

        self.click_apply_button()

    def apply_who_filter(self, filters: dict):
        """Apply the 'Who' filter based on the provided filters."""
        if "who" not in filters:
            return

        if "age_from" not in filters["who"] and "age_to" not in filters["who"]:
            return

        wait = WebDriverWait(self.driver, LOAD_WAIT_TIME)
        who_filter = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Filter Who unselected"]'))
        )
        who_filter.click()
        logger.info("Clicked Who filter")
        time.sleep(LOAD_WAIT_TIME5)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "an-focus-trap")))
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "filter-sections")))

        if "age_from" in filters["who"]:
            age_from_xpath = '//input[@aria-label="Age range from"]'
            age_from_input = WebDriverWait(self.driver, LOAD_WAIT_TIME5).until(
                EC.presence_of_element_located((By.XPATH, age_from_xpath))
            )

            age_from_input.clear()
            age_from_input.send_keys(filters["who"]["age_from"])
            print(f"Age from: {filters['who']['age_from']}")

        if "age_to" in filters["who"]:
            age_to_xpath = '//input[@aria-label="Age range to"]'
            age_to_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, age_to_xpath))
            )

            age_to_input.clear()
            age_to_input.send_keys(filters["who"]["age_to"])
            print(f"Age to: {filters['who']['age_to']}")

        self.click_apply_button()

    def apply_where_filter(self, filters: dict):
        """Apply the 'Where' filter based on the provided filters."""
        if "where" not in filters:
            return

        if "locations" not in filters["where"]:
            return

        if not len(filters["where"]["locations"]) > 0:
            return

        wait = WebDriverWait(self.driver, LOAD_WAIT_TIME)
        where_filter = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Filter Where unselected"]'))
        )
        where_filter.click()
        logger.info("Clicked Where filter")
        time.sleep(LOAD_WAIT_TIME5)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "an-focus-trap")))
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "filter-sections")))

        view_more_element = WebDriverWait(self.driver, LOAD_WAIT_TIME).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listbox__show-more-link"))
        )
        view_more_element.click()
        logger.info("Clicked View more element")
        time.sleep(LOAD_WAIT_TIME5)

        location_checkboxes = WebDriverWait(self.driver, LOAD_WAIT_TIME).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//div[@class='filter-sections filter-sections-checkbox']/fieldset/legend[text()='Location (Center)']/../div[@class='checkbox-group']//input[@type='checkbox']",  # noqa: E501
                )
            )
        )
        time.sleep(LOAD_WAIT_TIME)

        for checkbox in location_checkboxes:
            label = checkbox.find_element(
                By.XPATH, "./following-sibling::span[@class='checkbox__text']/span"
            ).text
            if utils.is_contains(label, filters["where"]["locations"]):
                checkbox.click()
                print(f"Clicked checkbox: {label}")
                time.sleep(LOAD_WAIT_TIME1)

        logger.info("Clicked location checkboxes")

        self.click_apply_button()

        logger.info("Applied where filter")

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page and count the number of pages and time taken."""
        start_time = time.time()
        old_position = self.driver.execute_script("return window.pageYOffset;")
        page_count = 0

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(LOAD_WAIT_TIME3)
            new_position = self.driver.execute_script("return window.pageYOffset;")
            if new_position == old_position:
                break
            old_position = new_position
            page_count += 1

            if page_count % 10 == 0:
                print(f"Pages scrolled: {page_count}")

        end_time = time.time()
        time_taken = end_time - start_time

        logger.info("Total pages scrolled: %s", page_count)
        logger.info("Time taken to scroll: %.2f seconds", time_taken)

    def click_apply_button(self):
        """Click the Apply button."""
        apply_button = self.driver.find_element(
            By.XPATH,
            '//div[@class="activity-filter-footer "]//button[@class="btn btn-strong btn--sm activity-filter-footer__apply-btn"]',  # noqa: E501
        )
        apply_button.click()
        time.sleep(LOAD_WAIT_TIME)
        logger.info("Clicked Apply button")

    def downloaded_file_exists(self, data_save_format: DataSaveFormat) -> bool:
        """Check if the downloaded file exists."""
        file_path = self.get_page_source_file_path()
        return os.path.exists(file_path)

    def extract_data(self, data_save_format: DataSaveFormat, filters: dict) -> None:
        """Extract the data from the downloaded file."""
        file_path = self.get_page_source_file_path()
        activities, skipped_activities = extract_activities_from_page_source(file_path, filters)
        self.save_data(activities, data_save_format)
        self.save_skipped_data(skipped_activities, data_save_format)
        logger.info("Extracted data from the downloaded file")
