import configparser
import logging
import re
from urllib.parse import urljoin

from selenium.webdriver.common.keys import Keys


class Connector:
    def __init__(self, driver, settings):
        self.driver = driver
        self.settings = settings

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
    def __init__(self, settings_file="settings.ini"):
        self.settings_file = settings_file

    def read(self):
        settings = configparser.RawConfigParser()
        settings.read(self.settings_file, encoding="UTF-8")
        return settings

    def write(self, new_settings):
        with open(self.settings_file, 'w', encoding='UTF-8') as settings_fp:
            new_settings.write(settings_fp)
