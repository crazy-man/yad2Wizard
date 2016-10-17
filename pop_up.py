import logging
from collections import defaultdict
from logging.handlers import RotatingFileHandler

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from common import Settings, Connector


class PopUpper:
    def __init__(self, driver, settings):
        self.driver = driver
        self.settings = settings
        self.main_tab = self.driver.current_window_handle
        self.curr_tab = self.main_tab
        self.result = defaultdict(lambda: 0)

    def pop_up_sections(self):
        self.main_tab = self.driver.current_window_handle
        self.driver.get(self.settings["Pages"]["order"])
        sections_container = self.driver.find_element_by_xpath(self.settings["Selectors"]["order_table_xpath"])
        active_sections = sections_container.find_elements_by_tag_name("a")
        self.result = defaultdict(lambda: 0)
        if not len(active_sections):
            warning = "No active sections found for this account"
            logging.warning(warning)
            self.result["warning"] = warning
            return self.result

        for section_link in active_sections:
            section_link.send_keys(Keys.CONTROL + Keys.SHIFT + Keys.RETURN)
            self.curr_tab = self.driver.window_handles[-1]
            self.driver.switch_to_window(self.curr_tab)
            self.pop_up_ads()
            self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
            self.driver.switch_to_window(self.main_tab)
        return self.result

    def pop_up_ads(self):
        ads_container = self.driver.find_element_by_xpath(self.settings["Selectors"]["ads_table_xpath"])
        # here we exclude the first and the last row, since those are just table header and footer
        ads_rows = ads_container.find_elements_by_tag_name("tr")[1:-1]
        for ad_row in ads_rows:
            ad_row.click()
            # now, row should be expanded, let's find pop-up button inside IFRAME (WTF?!)
            iframe = ads_container.find_element_by_tag_name('iframe')
            self.driver.switch_to_frame(iframe)
            try:
                pop_up_btn = self.driver.find_element_by_xpath(self.settings["Selectors"]["pop_up_btn_xpath"])
                # yeah :)
                pop_up_btn.click()
                self.result["popped_up"] += 1
            except NoSuchElementException:
                # happens when ad is already popped up, need to wait for the next iteration
                try:
                    self.driver.find_element_by_xpath(self.settings["Selectors"]["pop_up_btn_disabled_xpath"])
                    self.result["already_popped_up"] += 1
                except NoSuchElementException:
                    # should not happen..., button was not found at all.., maybe selectors where changed or whatever
                    self.result["internal_error"] += 1

            # let's go back to current tab
            self.driver.switch_to_window(self.curr_tab)
            ad_row.find_element_by_link_text("סגור").click()


def main():
    log_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    logFile = 'pop_up.log'

    my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024,
                                     backupCount=0, encoding="UTF-8", delay=0)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    app_log = logging.getLogger()
    app_log.setLevel(logging.INFO)

    app_log.addHandler(my_handler)

    logging.info("Starting pop upper")

    driver = webdriver.Chrome()
    settings = Settings().read()

    connector = Connector(driver, settings)
    pop_upper = PopUpper(driver, settings)

    try:
        connector.login()
        res = pop_upper.pop_up_sections()
        connector.logout()
    finally:
        driver.close()
    msg = "Result: {}".format(", ".join(["{}: {}".format(k, v) for k, v in res.items()]))
    logging.info(msg)
    print(msg)

if __name__ == '__main__':
    main()
