import seleniumwire.undetected_chromedriver as uc
import re
# import api
# from selenium import webdriver
import random
import time
from seleniumwire.webdriver import ChromeOptions
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# hostname, port_http, proxy_user, proxy_pass = api.get_proxy_info("zMbqYVRQFcnLRhBhHYVXDgxo2LDgInHu")
# PROXY_1 = "http://"+proxy_user+":"+proxy_pass+"@"+hostname+":"+port_http
# PROXY_2 = "https://"+proxy_user+":"+proxy_pass+"@"+hostname+":"+port_http
# Set the path to the Chromedriver
# options = webdriver.ChromeOptions()
# options.add_argument(f'--proxy-server={PROXY}')

 
# options = {
#      'proxy': {'http': 'http://brd-customer-hl_6eaba908-zone-residential_proxy1-country-vn:721aj4p8gdc3@brd.superproxy.io:33335',
#      'https': 'http://brd-customer-hl_6eaba908-zone-residential_proxy1-country-vn:721aj4p8gdc3@brd.superproxy.io:33335'},
#  }


# options = {
#      'proxy': {'http': PROXY_1,
#      'https': PROXY_2},
#  }

# Initialize the Chrome driver
# driver = webdriver.Chrome(seleniumwire_options=options)


def type_like_human(element, text, delay_range=(0.1, 0.3)):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))  # Random delay between key presses

def web_driver_wait(driver: uc.Chrome, locator: By, locator_value, timeout = 30):
    try:
        elem = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((locator, locator_value))
        )
        print("Wait complete with detected objects")
        return elem
    except :
        raise Exception("Wait timed out")

def driver_wait_full_page(driver: uc.Chrome, timeout = 30):
    try:
        WebDriverWait(driver, timeout).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        print("Wait complete with full page loaded")
    except :
        raise Exception("Wait timed out")


def sign_in(driver: uc.Chrome, username, password):
    account_btn = web_driver_wait(driver, By.ID, "nav-link-accountList")
    account_btn.click()
    email_input = web_driver_wait(driver, By.XPATH, "//input[@id='ap_email']")
    type_like_human(email_input, username, delay_range=(0.2, 0.5))
    continue_btn = driver.find_element(By.XPATH, "//span[@id='continue']")
    continue_btn.click()
    password_input = web_driver_wait(driver, By.CSS_SELECTOR, "#ap_password")
    type_like_human(password_input, password, delay_range=(0.2, 0.5))
    signin_btn = driver.find_element(By.XPATH, value="//span[@id='auth-signin-button']")
    signin_btn.click()

def search_product(driver: uc.Chrome, product_name):
    search_bar = web_driver_wait(driver, By.ID, "twotabsearchtextbox")
    search_bar.clear()
    print(f"Typing {product_name}")
    type_like_human(search_bar, product_name, delay_range=(0.2, 0.5))
    search_bar.send_keys("\n")

def get_all_products_links(driver: uc.Chrome):
    elems = web_driver_wait(driver, By.XPATH, "//div[@class='s-desktop-width-max s-desktop-content s-opposite-dir s-wide-grid-style sg-row']")
    driver.implicitly_wait(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    global product_links
    elems = driver.find_elements(By.XPATH, "//span//a[@class='a-link-normal s-no-outline']")
    for ele in elems:
        product_links.append(ele.get_attribute("href"))
    driver.implicitly_wait(3)
    try:
        next_btn = web_driver_wait(driver, By.XPATH, "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator']")
        next_btn.click()
        print(product_links)
        get_all_products_links(driver)
    except Exception as e:
        print(e)
        # print("Reached the last page. All products' links are collected.")
        # return 

def get_product_detail(driver: uc.Chrome, href):
    driver.get(href)
    driver_wait_full_page(driver)
    product_name = driver.find_element(By.XPATH, "//span[@id='productTitle']")
    price_raw = driver.find_element(By.XPATH, "//div[@id='apex_desktop']//div[@data-csa-c-slot-id='apex_dp_center_column']//div[@data-csa-c-slot-id='apex_dp_center_column']//div[@id='corePriceDisplay_desktop_feature_div']//div[@class='a-section a-spacing-none aok-align-center aok-relative']//span[@class='aok-offscreen']").text
    price = price_raw.split()
    
    string = 'value is between 5 and 10'
    m = re.match(r'value is between (.*) and (.*)', string)
    print(m.group(1), m.group(2))

product_links = []

def main():
    global product_links
    driver = uc.Chrome()
    driver.get("https://amazon.com")
    sign_in(driver, "mailto:diepbaothien10x@gmail.com", "thien1")
    search_product(driver, "Gaming Chair")
    get_all_products_links(driver)
    time.sleep(500)
    driver.quit()

if __name__ == "__main__":
  main()