import configparser
import logging
import os
import re
from logging.handlers import RotatingFileHandler

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def home(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), filename))


def init_logging(filename):
    log_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    log_file = home(os.path.splitext(filename)[0] + '.log')
    my_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5 * 1024 * 1024,
                                     backupCount=0, encoding="UTF-8", delay=0)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)
    app_log = logging.getLogger()
    app_log.setLevel(logging.INFO)
    app_log.addHandler(my_handler)


def prettify_string(string):
    return ' '.join(x.capitalize() or '_' for x in string.split('_'))


class Connector:
    def __init__(self, driver=None, settings=None):
        self.driver = webdriver.Chrome() if driver is None else driver
        self.settings = Settings().read() if settings is None else settings

    def login(self, username=None, password=None):
        if not username:
            username = self.settings["User"]["name"]
        if not password:
            password = self.settings["User"]["pass"]

        self.driver.get(self.settings["Pages"]["login"])

        username_field = self.driver.find_element_by_id("userName")
        username_field.clear()
        username_field.send_keys(username)

        password_field = self.driver.find_element_by_id("password")
        password_field.clear()
        password_field.send_keys(password)

        password_field.send_keys(Keys.RETURN)

        if self.driver.current_url != self.settings["Pages"]["order"]:
            logging.info("Failed to log in, current url: " + self.driver.current_url)
            raise RuntimeError("Failed to log in")

    def logout(self):
        self.driver.get(self.settings["Pages"]["logout"])
        if self.driver.current_url != self.settings["Domain"]["home"]:
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
