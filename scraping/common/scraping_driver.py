import os
from get_chrome_driver import GetChromeDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ScrapingDriver():

    def __init__(self):
        self.chrome_driver_dir = 'chromedriver_linux64'
        self.chrome_driver_file = self.chrome_driver_dir + '/chromedriver'
        self.option = Options()
        self.option.add_argument('--disable-notifications')
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('--disable-dev-shm-usage')
        # self.option.add_argument('--headless')
        chrome_prefs = {}
        self.option.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}

    def download_driver(self):
        if not os.path.exists(self.chrome_driver_file):
            download_driver = GetChromeDriver()
            download_driver.auto_download(output_path=self.chrome_driver_dir, extract=True)

    def execute_driver(self):
        driver = webdriver.Chrome(executable_path=self.chrome_driver_file, options=self.option)
        return driver
