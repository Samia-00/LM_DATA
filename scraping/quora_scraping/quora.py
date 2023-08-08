import json
import time
from app_configs.common import CREDENTIALS, FAILD_TOLERATE_POST_LIST
from app_configs.constants import DELAY_LONG
from app_configs.quora import QUORA_MAIN_SITE
from scraping.common.scraping_driver import ScrapingDriver
from scraping.quora_scraping.login import QuoraLogin
from scraping.quora_scraping.scraping_posts import QuoraPostsURLScraper, QuoraPostsDataScraper
from utils.error_handling import ErrorLogger


def main():

    scraping_driver = ScrapingDriver()

    scraping_driver.download_driver()

    driver = scraping_driver.execute_driver()

    driver.get(QUORA_MAIN_SITE)
    driver.maximize_window()
    time.sleep(DELAY_LONG)

    quara_login = QuoraLogin(CREDENTIALS['quora']['email'], CREDENTIALS['quora']['password'])
    quara_login.login(driver)

    count_failed = 0
    count_page = 1

    this_filename = '_'.join(__file__.split('/')[-2:])[:-3]
    error_logger = ErrorLogger(this_filename)

    while True:

        try:
            quora_posts_url_scraper = QuoraPostsURLScraper()
            quora_posts_data_scraper = QuoraPostsDataScraper()

            if count_failed>FAILD_TOLERATE_POST_LIST:
                break

            posts_data = quora_posts_url_scraper.get_posts_url(driver)
            for post in posts_data[:5]:
                quora_posts_data_scraper.get_posts_data(driver, post)

            quora_posts_url_scraper.click_to_load_new_posts(driver)

        except Exception as e:
            count_failed+=1
            error_logger.logger.exception(e)

        print(f'\n\nEnd {count_page} page scraping!\n\n')
        count_page += 1
        time.sleep(DELAY_LONG)
        driver.get(QUORA_MAIN_SITE)

