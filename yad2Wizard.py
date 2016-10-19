import logging
import random

import datetime
from PyQt5 import uic, QtWidgets
import sys
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import qApp
from selenium import webdriver

from common import Validate, Settings, Connector, prettify_string, init_logging
from pop_up import PopUpper


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui/yad2Wizard.ui', self)
        self.settings = Settings().read()
        self.pop_upper = None
        self.license = ""
        self.version = "0.0.0"
        self.timer = None
        self.init_misc()
        self.init_menu()
        self.init_buttons()
        self.show()
        self.show_message("Initialized")

    def __del__(self):
        # cancel background thread(if running)
        if self.timer:
            try:
                self.timer.cancel()
            except:
                self.timer = None

    def init_misc(self):
        with open('LICENSE', 'r') as l:
            self.license = l.read()
        with open('VERSION', 'r') as v:
            self.version = v.read()
        self.username.setText(self.settings["User"]["name"])
        self.password.setText(self.settings["User"]["pass"])

    def init_menu(self):
        self.actionExit.triggered.connect(qApp.quit)
        self.actionAbout.triggered.connect(self.show_about_dialog)

    def show_message(self, msg):
        logging.info(msg)
        self.statusBar.showMessage(msg)

    def init_buttons(self):
        self.test_credentials.clicked.connect(self.test_credentials_click)
        self.save_credentials.clicked.connect(self.save_credentials_click)
        self.pop_up_now.clicked.connect(self.pop_up_now_click)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def show_about_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("yad2Wizard v{}".format(self.version))
        msg.setInformativeText("Copyright © 2016 Constantine Dubovenko")
        msg.setWindowTitle("About yad2Wizard")
        msg.setDetailedText(self.license)
        spacer = QSpacerItem(500, 0)
        msg.layout().addItem(spacer)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        msg.exec_()

    def test_credentials_click(self):
        self.show_message("Testing credentials")
        username = self.username.text()
        try:
            Validate.email(username)
        except ValueError as ve:
            self.show_message(str(ve))
            return

        password = self.password.text()
        try:
            Validate.password(password)
        except ValueError as ve:
            self.show_message(str(ve))
            return

        driver = webdriver.Chrome()
        connector = Connector(driver, self.settings)

        try:
            connector.login(username, password)
            connector.logout()
            self.show_message("Connected Successfully!")
        except RuntimeError as re:
            self.show_message(str(re))
        finally:
            driver.close()

    def save_credentials_click(self):
        self.show_message("Saving credentials")
        username = self.username.text()
        try:
            Validate.email(username)
        except ValueError as ve:
            self.show_message(str(ve))
            return

        password = self.password.text()
        try:
            Validate.password(password)
        except ValueError as ve:
            self.show_message(str(ve))
            return
        self.settings["User"]["name"] = username
        self.settings["User"]["pass"] = password
        try:
            Settings().write(self.settings)
            self.show_message("Saved Successfully!")
        except Exception as e:
            self.show_message(str(e))
            return

    def pop_up_now_click(self):
        self.show_message("Starting to pop up")
        if self.timer:
            try:
                self.timer.cancel()
            except:
                self.timer = None

        self.run_periodically()

    def run_periodically(self):
        self.pop_upper = PopUpper()
        res = self.pop_upper.run()
        msg = "Result: {}".format(", ".join(["{}: {}".format(prettify_string(k), v) for k, v in res.items()]))
        timeout = self.settings.getfloat("Timeout", "period") * 60 + 60 * random.randint(1, self.settings.getint("Timeout", "random"))
        next_run = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        self.show_message(msg + " | Next run at {}".format(next_run.strftime("%Y-%m-%d %H:%M:%S")))
        self.timer = threading.Timer(timeout, self.run_periodically)
        self.timer.start()

if __name__ == '__main__':
    init_logging(__file__)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
