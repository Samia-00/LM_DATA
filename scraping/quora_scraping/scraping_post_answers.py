import time
import selenium
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from app_configs.common import FAILD_TOLERATE_RELATED_QUESTION
from app_configs.constants import DELAY_SHORT
from scraping.common.helpers import Helpers


class QuoraPostsAnsScraper:
    def __init__(self):
        self.helpers = Helpers()

    def scrape_related_ques(self, driver, posts_ans_selector):
        related_ques = []
        related_ques_selector = '#mainContent .dom_annotate_related_questions'
        faild_count = 0
        while True:
            try:
                related_ques_element = driver.find_element(By.CSS_SELECTOR, related_ques_selector)
                related_ques = related_ques_element.find_elements(By.CSS_SELECTOR, posts_ans_selector)
                related_ques = [i.text for i in related_ques]
                break
            except NoSuchElementException as e:
                self.helpers.scroll_to_bottom_js(driver, DELAY_SHORT)
                faild_count+=1
            if faild_count>FAILD_TOLERATE_RELATED_QUESTION:
                break
        return related_ques

    def click_read_more(self, driver):
        more_btns_selector = 'span.qt_read_more'
        more_btns = driver.find_elements(By.CSS_SELECTOR, more_btns_selector)
        for btn in more_btns:
            self.helpers.scroll_to_element_js(driver, btn)
            self.helpers.click_to_btn_js(driver, btn)

    def scrape_posts_ans_text(self, driver, posts_ans_selector):
        posts_ans = driver.find_elements(By.CSS_SELECTOR, posts_ans_selector)
        post_details_data = [post_ans.text for post_ans in posts_ans]
        if post_details_data:
            post_details_data = post_details_data[1:]
        return post_details_data

    def get_posts_ans(self, driver):
        posts_ans_selector = '.q-box qu-userSelect--text'.replace(' ', '.')
        related_ques = self.scrape_related_ques(driver, posts_ans_selector)
        self.click_read_more(driver)
        post_details_data = self.scrape_posts_ans_text(driver, posts_ans_selector)
        return post_details_data, related_ques

