import os

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager


class ChromeBrowser:
    driver: WebDriver

    def __init__(self, headless: bool = False, time_to_wait: int = 10):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("download.default_directory=" + os.getcwd() + os.path.sep)
        options.add_argument("--start-maximized")
        prefs = {
            "profile.default_content_settings.popups": 0,
            'download.default_directory': os.getcwd() + os.path.sep,
            "directory_upgrade": True
        }
        options.add_experimental_option('prefs', prefs)
        options.page_load_strategy = "normal"  # wait until all resources are fetched
        self.driver = Chrome(options=options, service=Service(ChromeDriverManager().install()))
        if time_to_wait > 0:
            self.driver.implicitly_wait(time_to_wait)

    def close(self):
        if self.driver:
            self.driver.close()

    def navigate(self, url: str, timeout: float = -1, wait_seconds: int = 10, validate: bool = True) -> bool:
        if timeout > 0:
            self.driver.set_page_load_timeout(timeout)
        self.driver.get(url)
        for second in range(0, wait_seconds):
            if self.driver.current_url == url:
                break
            else:
                continue
        if validate and self.driver.current_url != url:
            print("failed to navigate. current: {}, expected: {}".format(self.driver.current_url, url))
            return False
        return True

    def get_page_source(self) -> str:
        return self.driver.page_source

    def get_url(self) -> str:
        return self.driver.current_url

    def find_elements_by_id(self, element_id: str) -> [WebElement]:
        return self.find_elements(By.ID, element_id)

    def find_elements_by_classname(self, element_classname: str) -> [WebElement]:
        return self.find_elements(By.CLASS_NAME, element_classname)

    def find_elements_by_xpath(self, xpath: str) -> [WebElement]:
        return self.find_elements(By.XPATH, xpath)

    def find_elements_by_css_selector(self, selector: str) -> [WebElement]:
        return self.find_elements(By.CSS_SELECTOR, selector)

    def find_elements(self, by: str, criteria: str) -> [WebElement]:
        result = self.driver.find_elements(by, criteria)
        if len(result) == 0:
            raise Exception("failed to find element by {} as {}".format(by, criteria))
        return result
