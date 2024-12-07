from scraper.amazon_scraper_class import AmazonPWrightScraper
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
    scraper = AmazonPWrightScraper(hasSignIn=False, productNames=["Gaming Chair", "Gaming Headset"],account={"username": "diepbaothien10x@gmail.com", "password": "thien1"}, headless=False)
    await scraper.activate_scraper()

if __name__ == "__main__":
    asyncio.run(main())