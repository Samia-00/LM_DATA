import os
import time
from telnetlib import EC
import pendulum
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from accessing_db.mongodb_accessing import DataWriter, DataReader
from app_configs.common import FILE_PAGE_NOT_FOUND_TEXT, DIR_RESOURCES, FAILD_TOLERATE_NEW_POST, DIR_REPORT, FILE_LOG
from app_configs.constants import DELAY_LONG, DELAY_SHORT
from app_configs.mongo import COLLECTION_NAME_SCRAPED_DATA
from scraping.common.helpers import Helpers
from scraping.quora_scraping.scraping_comments import QuoraPostsCommentScraper
from scraping.quora_scraping.scraping_post_answers import QuoraPostsAnsScraper
from utils.error_handling import ErrorLogger


class QuoraPostsDataScraper:
    def __init__(self):
        self.helpers = Helpers()
        self.data_writer = DataWriter()
        self.count_saved = 0
        self.count_unable_to_scrape = 0
        self.this_filename = '_'.join(__file__.split('/')[-2:])[:-3]
        self.error_logger = ErrorLogger(self.this_filename)
        os.makedirs(DIR_REPORT, exist_ok=True)
    def check_page_not_found(self, driver):

        is_page_not_found = False
        try:
            post_url_selector = 'body'
            text = driver.find_element(By.CSS_SELECTOR, post_url_selector).text
            with open(f'{DIR_RESOURCES}{FILE_PAGE_NOT_FOUND_TEXT}') as file:
                page_not_found = file.readlines()
            for i in page_not_found:
                not_found_txt = i.strip().replace('\n', '')
                if not_found_txt in text.strip():
                    is_page_not_found = True
                    break
        except Exception as e:
            self.error_logger.logger.exception(e)

        return is_page_not_found

    def get_posts_data(self, driver, post):
        driver.get(post["post_url"])
        is_page_not_found = self.check_page_not_found(driver)

        if is_page_not_found:
            self.count_unable_to_scrape+=1
            print(f'{self.count_unable_to_scrape}. Unable to sctape : {post["post_url"]}')
            time.sleep(DELAY_LONG)
            return None

        quora_posts_ans_scraper = QuoraPostsAnsScraper()
        post_ans_data, related_ques_data = quora_posts_ans_scraper.get_posts_ans(driver)
        post['post_answers'] = post_ans_data
        post['related_questions'] = related_ques_data
        quora_posts_comment_scraper = QuoraPostsCommentScraper()
        comment_data = quora_posts_comment_scraper.get_comments_data(driver)
        post['comment_texts'] = comment_data
        post['scraped_at'] = pendulum.now().in_timezone('UTC')

        id = self.data_writer.save_data_to_collection(COLLECTION_NAME_SCRAPED_DATA, post)
        self.count_saved+=1

        with open(f'{DIR_REPORT}{FILE_LOG}', 'a') as file:
            try:
                print(f'{post["scraped_at"].strftime("%Y-%m-%d %H:%M:%S")} : {self.count_saved}. {post["question"]}')
                file.write(f'{post["scraped_at"].strftime("%Y-%m-%d %H:%M:%S")} : {self.count_saved}. {post["question"]}\n')
            except:
                print(f'{post["scraped_at"].strftime("%Y-%m-%d %H:%M:%S")} : {self.count_saved}. {id}')
                file.write(f'{post["scraped_at"].strftime("%Y-%m-%d %H:%M:%S")} : {self.count_saved}. {id}\n')


class QuoraPostsURLScraper:
    def __init__(self):
        self.helpers = Helpers()
        self.data_reader = DataReader()
        self.existing_posts_url = self.data_reader.get_scraped_url(30)
        self.this_filename = '_'.join(__file__.split('/')[-2:])[:-3]
        self.error_logger = ErrorLogger(self.this_filename)

    def scrape_post_url_time_question(self, post):
        data = {}


        # post_url_selector = '.TitleText___StyledCssInlineComponent-sc-1hpb63h-0 a'
        post_url_selector = '.q-box.Link___StyledBox-t2xg9c-0.dFkjrQ.answer_timestamp.qu-cursor--pointer.qu-hover--textDecoration--underline'
        # post_url_selector_data = post_url_selector.split('/answers/')
        # print(post_url_selector_data)
        # post_url_selector = 'a.q-box'
        # post_url_selector = '.answer_timestamp'

        data['post_url'] = post.find_element(By.CSS_SELECTOR, post_url_selector).get_attribute('href').split('/answers/')[0]
        # print(post.get_attribute("innerHTML"))
        # print(data['post_url'])
        if data['post_url'] in self.existing_posts_url:
            return False

        posted_at_selector = '.answer_timestamp'
        data['posted_at'] = post.find_element(By.CSS_SELECTOR, posted_at_selector).text
        post_title = '.q-text.puppeteer_test_question_title'
        data['question'] = post.find_element(By.CSS_SELECTOR, post_title).text

        return data

    def scrape_post_elements(self, driver):

        posts = []
        failed_count = 0

        while True:

            try:
                posts_selector = '.q-box dom_annotate_multifeed_bundle_AnswersBundle qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised'.replace( ' ', '.')
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, posts_selector)))
                posts = driver.find_elements(By.CSS_SELECTOR, posts_selector)
                break
            except:
                failed_count += 1
                time.sleep(DELAY_LONG)

            if failed_count > 5:
                break

        return posts

    def go_to_see_new_posts_btn(self, driver):
        feed_last_selector = '#mainContent .qu-color--white .qu-whiteSpace--nowrap'
        no_of_scroll = 0
        while True:
            try:
                feed_last = driver.find_element(By.CSS_SELECTOR, feed_last_selector)
                self.helpers.scroll_to_element_js(driver, feed_last)
                break
            except Exception as e:
                self.helpers.scroll_to_bottom_js(driver)
                no_of_scroll+=1

            if no_of_scroll > FAILD_TOLERATE_NEW_POST:
                break

    def get_posts_url(self, driver):

        self.go_to_see_new_posts_btn(driver)

        post_data = []
        posts = self.scrape_post_elements(driver)
        for post in posts:
            data = self.scrape_post_url_time_question(post)
            if data:
                post_data.append(data)
            else:
                print('Duplicated')
        return post_data

    def click_to_load_new_posts(self, driver):
        try:
            button_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "পৃষ্ঠাটি রিফ্রেশ করুন")]'))
            )
            self.helpers.click_to_btn_js(driver, button_element)
        except Exception as e:
            print("Error:", e)


        # try:
        #     # feed_last_selector = '#mainContent .qu-color--white .qu-whiteSpace--nowrap [role="button"]'
        #     # feed_last_selector = '.qu-color--white .qu-whiteSpace--nowrap[role="button"]'
        #     # feed_last_selector = '.q-box .qu-bg--blue.qu-tapHighlight--white.qu-textAlign--center.qu-cursor--pointer .qu-whiteSpace--nowrap'
        #     feed_last_selector = 'button.q-click-wrapper'
        #     refresh_btn = driver.find_element(By.CSS_SELECTOR, feed_last_selector)
        #     self.helpers.click_to_btn_js(driver, refresh_btn)
        # except Exception as e:
        #     self.error_logger.logger.exception(e)
        #     print('testing')
