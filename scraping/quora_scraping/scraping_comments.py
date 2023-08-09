from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraping.common.helpers import Helpers


class QuoraPostsCommentScraper:
    def __init__(self):
        self.helpers = Helpers()


    def click_to_more_comment(self, driver):
        failed_count = 0
        while True:
            try:
                more_comment = driver.find_element(By.CSS_SELECTOR, '.qu-display--flex.chFPbJ')
                self.helpers.scroll_to_element_js(driver, more_comment)
                self.helpers.click_to_btn_js(driver, more_comment)
            except:
                break

    def get_comments_data(self,driver):
        comment_data = []
        try:
            comment_btn_cls = '.dom_annotate_answer_action_bar_comment'
            comment_btn_selector = f'{comment_btn_cls} button'
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, comment_btn_selector)))
            comment_btns = driver.find_elements(By.CSS_SELECTOR, comment_btn_selector)

            for comment_btn in comment_btns:
                self.helpers.scroll_to_element_js(driver, comment_btn)
                self.helpers.click_to_btn_js(driver, comment_btn)
                self.click_to_more_comment(driver)

            comment_texts = [i.text for i in driver.find_elements(By.CSS_SELECTOR,'.q-box.qu-borderRadius--small .qu-px--medium.qu-pt--small.qu-bg--raised .q-relative .q-text .q-box.qu-userSelect--text')]
            comment_data.append(comment_texts)

        except Exception as e:
            print(e)

        return comment_data