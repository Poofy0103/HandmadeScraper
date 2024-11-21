import seleniumwire.undetected_chromedriver as uc
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumUtils:
    @staticmethod
    def type_like_human(element, text, delay_range=(0.1, 0.3)):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))  # Random delay between key presses

    @staticmethod
    def web_driver_wait(driver: uc.Chrome, locator: By, locator_value, timeout = 30):
        try:
            elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((locator, locator_value))
            )
            print("Wait complete with detected objects")
            return elem
        except :
            raise Exception("Wait timed out")

    @staticmethod
    def driver_wait_full_page(driver: uc.Chrome, timeout = 30):
        try:
            WebDriverWait(driver, timeout).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            print("Wait complete with full page loaded")
        except :
            raise Exception("Wait timed out")

    @staticmethod
    def scroll_to_bottom(driver: uc.Chrome):
        driver.implicitly_wait(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")