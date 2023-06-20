import json
import os
import pickle
import time
from csv import DictReader
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from app_configs.common import DIR_RESOURCES
from app_configs.constants import DELAY_SHORT
from app_configs.quora import DIRNAME_COOKIES
from utils.error_handling import ErrorLogger


class QuoraLogin:

    def __init__(self, user_email, user_password):
        self.user_email = user_email
        self.user_password = user_password
        self.this_filename = '_'.join(__file__.split('/')[-2:])[:-3]
        self.error_logger = ErrorLogger(self.this_filename)


    def entering_input_value(self, driver, css_selector, input_value):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, css_selector)))
        log_In_input = driver.find_element(By.NAME, css_selector)
        log_In_input.send_keys(input_value)
        time.sleep(DELAY_SHORT)

    def entering_email(self, driver):
        email_selector = "email"
        self.entering_input_value(driver, email_selector, self.user_email)

    def entering_password(self, driver):
        pass_selector = "password"
        self.entering_input_value(driver, pass_selector, self.user_password)

    def solve_recaptcha(self, driver):
        is_recaptcha = True
        inp = input('Enter random character during solving recaptcha: ')
        if inp:
            return is_recaptcha

    def click_to_login_btn(self, driver):
        login_btn_cls = '.q-flex qu-justifyContent--space-between qu-alignItems--center'.replace(' ', '.')
        login_btn_selector = f'{login_btn_cls} button'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, login_btn_selector))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, login_btn_selector)))
        btn_next = driver.find_element(By.CSS_SELECTOR, login_btn_selector)
        time.sleep(DELAY_SHORT)
        btn_next.click()
        time.sleep(DELAY_SHORT)

    def read_cookies_value(self, file):
        if file.split('.')[-1] == 'csv':
            with open(file, encoding='utf-8') as f:
                dict_reader = DictReader(f)
                list_of_dict = list(dict_reader)
        else:
            with open(file) as f:
                dict_reader = json.load(f)
                list_of_dict = list(dict_reader)
        return list_of_dict

    def login_using_cookies(self, driver, file_path):
        with open(file_path, "rb") as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        print(f"Login in Using Cookies")

    def save_cookies(self,driver,file_path):
        with open(file_path, "wb") as file:
            pickle.dump(driver.get_cookies(), file)

    def login(self, driver):

        quora_cookies_path = f'{DIR_RESOURCES}/{DIRNAME_COOKIES}'

        if os.path.exists(quora_cookies_path):
            try:
                self.login_using_cookies(driver, quora_cookies_path)
                return True
            except Exception as e:
                self.error_logger.logger.exception(e)

        self.entering_email(driver)

        self.entering_password(driver)

        is_recaptcha = self.solve_recaptcha(driver)

        self.save_cookies(driver, quora_cookies_path)

        if is_recaptcha:
            return True

        self.click_to_login_btn(driver)





