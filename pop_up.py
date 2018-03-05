#!/usr/bin/env python3

import logging
from collections import defaultdict

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from common import Settings, Connector, prettify_string, init_logging, get_chrome_options


class PopUpper:
    def __init__(self, driver=None, settings=None):
        self.driver = webdriver.Chrome(chrome_options=get_chrome_options()) if driver is None else driver
        self.settings = Settings().read() if settings is None else settings
        self.connector = Connector(self.driver, self.settings)

        self.result = defaultdict(lambda: 0)

    def pop_up_ads(self):
        ads_container = self.driver.find_element_by_css_selector("div.order-items")
        # here we exclude the first and the last row, since those are just table header and footer
        ads_rows = ads_container.find_elements_by_css_selector("a.item")
        if len(ads_rows) == 0:
            warning = "No ads found for this account"
            logging.warning(warning)
            self.result["warning"] = warning
            return self.result

        ads_links = [r.get_attribute("href") for r in ads_rows]
        for ad_link in ads_links:
            self.driver.get(ad_link)
            try:
                pop_up_btn = self.driver.find_element_by_class_name("jump")
            except NoSuchElementException:
                # should not happen..., button was not found at all.., maybe selectors where changed or whatever
                self.result["internal_error"] += 1

            if "grayout" in pop_up_btn.get_attribute("class"):
                self.result["already_popped_up"] += 1
            else:
                # yeah :)
                pop_up_btn.click()
                # let the request to be sent, before we continue in a loop
                try:
                    WebDriverWait(self.driver, self.settings.getint("Misc", "alert_timeout")).until(
                        expected_conditions.alert_is_present(),
                        'Timed out waiting for confirmation popup to appear.')

                    alert = self.driver.switch_to_alert()
                    alert.accept()
                    logging.info("alert accepted")
                    self.result["popped_up"] += 1
                except TimeoutException:
                    self.result["pop_up_timeout"] += 1

        return self.result

    def run(self):
        try:
            self.connector.login()
            res = self.pop_up_ads()
            self.connector.logout()
        except:
            raise
        finally:
            self.driver.close()
        return res


def main():
    init_logging(__file__)
    logging.info("Starting pop upper")

    pop_upper = PopUpper()
    res = pop_upper.run()

    msg = "Result: {}".format(", ".join(["{}: {}".format(prettify_string(k), v) for k, v in res.items()]))
    logging.info(msg)


if __name__ == '__main__':
    main()
