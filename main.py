from scraper.scraper_factory import ScraperFactory
import asyncio

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

async def main():
    scraper = ScraperFactory()
    # finance_scraper = scraper.get_scraper(platform = "finance", hasSignIn=False, stockCodes=["DBC", "SAB", "VNM", "NTP", "BMP"], headless=False, timeRange='01-01-2019 - 31-12-2024')
    # await finance_scraper.scraping_driver()
    # news_scraper = scraper.get_scraper(platform = "news", hasSignIn=False, stockCodes=["DBC", "SAB", "VNM", "NTP", "BMP"], headless=False, timeRange="01/01/2019 - 31/12/2024")
    # await news_scraper.scraping_driver()
    # macro_scraper = scraper.get_scraper(platform = "macro", hasSignIn=False, headless=False, timeRange="01/01/2019 - 31/12/2024")
    # await macro_scraper.scraping_driver()
    travelling_scraper = scraper.get_scraper(platform = "travelling", hasSignIn=False, stockCodes=["Ha Noi city"], scroll_page_attempt=10, headless=False, queuesNum=5)
    await travelling_scraper.scraping_driver()

if __name__ == "__main__":
    asyncio.run(main())