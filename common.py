import configparser
import logging
import os
import re
import urllib
from logging.handlers import RotatingFileHandler

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def home(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), filename))


def get_chrome_options():
    mobile_emulation = {
        "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument("window-size=380,660")
    return chrome_options


def init_logging(filename):
    log_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    log_file = home(os.path.splitext(filename)[0] + '.log')
    file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5 * 1024 * 1024,
                                     backupCount=0, encoding="UTF-8", delay=0)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    app_log = logging.getLogger()
    app_log.setLevel(logging.INFO)
    app_log.addHandler(file_handler)
    app_log.addHandler(console_handler)


def prettify_string(string):
    return ' '.join(x.capitalize() or '_' for x in string.split('_'))


class Connector:
    def __init__(self, driver=None, settings=None):
        self.driver = webdriver.Chrome(chrome_options=get_chrome_options()) if driver is None else driver
        self.settings = Settings().read() if settings is None else settings

    def login(self, username=None, password=None):
        if not username:
            username = self.settings["User"]["name"]
        if not password:
            password = self.settings["User"]["pass"]

        self.driver.get(self.settings["Pages"]["login"])
        username_field = self.driver.find_element_by_id(self.settings["Elements"]["login_username_id"])
        username_field.clear()
        username_field.send_keys(username)

        password_field = self.driver.find_element_by_id(self.settings["Elements"]["login_password_id"])
        password_field.clear()
        password_field.send_keys(password)

        self.driver.find_element_by_class_name("login-button").click()
        # selenium won't wait till the page is loaded. for now, just go to sleep for a while(might be dangerous):
        time.sleep(self.settings.getfloat("Misc", "request_timeout"))
        if urllib.parse.urlparse(self.driver.current_url).path != urllib.parse.urlparse(self.settings["Pages"]["order"]).path:
            logging.info("Failed to log in, current url: " + self.driver.current_url)
            raise RuntimeError("Failed to log in")

    def logout(self):
        self.driver.get(self.settings["Pages"]["logout"])
        time.sleep(self.settings.getfloat("Misc", "request_timeout"))
        if urllib.parse.urlparse(self.driver.current_url).path != urllib.parse.urlparse(self.settings["Pages"]["login"]).path:
            logging.info("Failed to log out, current url: " + self.driver.current_url)
            raise RuntimeError("Failed to log out")


class Validate:
    @staticmethod
    def email(email):
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        if match is None:
            raise ValueError('Invalid email address')

    @staticmethod
    def password(password):
        if not len(password):
            raise ValueError('Password cannot be empty')


class Settings:
    def __init__(self, settings_file=home("settings.ini")):
        self.settings_file = settings_file

    def read(self):
        settings = configparser.RawConfigParser()
        settings.read(self.settings_file, encoding="UTF-8")
        return settings

    def write(self, new_settings):
        with open(self.settings_file, 'w', encoding='UTF-8') as settings_fp:
            new_settings.write(settings_fp)
