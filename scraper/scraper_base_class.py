import seleniumwire.undetected_chromedriver as uc
from seleniumwire.webdriver import ChromeOptions

class BaseScraper:
    def __init__(self, headless=None, proxy=None):
        self.options = ChromeOptions()
        self.start_url = start_url
        self.selenium_options = dict()
        if headless:
            self.options.add_argument("--headless=new")
        if proxy:
            self.selenium_options['proxy'] = {'http': proxy, 'https': proxy}
        self.options.add_argument("--window-size=1280,800")
        self.options.add_argument("--disable-notifications")
        self.driver = uc.Chrome(options=self.options, seleniumwire_options=self.selenium_options)
        
    def load_page(self, url):
        self.driver.get(url)

    def close_browser(self):
        self.driver.quit()