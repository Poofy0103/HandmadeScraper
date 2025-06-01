from .web_scraper_class import WebsitePyppetScraper, WebsitePWrightScraper
from common.pyppeteer_utils import PyppeteerUtils
from common.playwright_utils import PlaywrightUtils
from playwright.async_api import Page
import asyncio
from pyppeteer import launch, browser, page
import uuid
from common.asyncioManager import AsyncioManager
from common.utils.ggcloud import CloudManager
import threading
from bs4 import BeautifulSoup, Comment
from tqdm.asyncio import tqdm
import os
from common.config import read_config
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn

class AmazonPWrightScraper(WebsitePWrightScraper):
    product_page = []
    isNextProduct = False
    condition = asyncio.Condition()
    cloudManager = CloudManager()
    config_values = read_config()

    def __init__(self, productNames: list, homepage, hasSignIn = False, account=dict(username=None, password=None), headless=False, proxy=None, maxQueueSize = 0, queuesNum = 2):
        super().__init__(headless, proxy)
        self.homepage = homepage
        self.account = account
        self.productNames = productNames
        self.hasSignIn = hasSignIn
        self.asyncManager = AsyncioManager(maxSize=maxQueueSize, queuesNum=queuesNum)

    async def scraping_driver(self):
        #Open another thread to monitor the task separately
        progress = Progress(
            TextColumn("[bold blue]{task.fields[label]}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn()
        )
        with Live(progress, refresh_per_second=3) as live:
            threading.Thread(target=self.asyncManager.monitor_task, args=(progress,), daemon=True).start()

            await self.initialize_browser()
            self.search_page = await self.initialize_page(self.main_context, "https://www.google.com")
            await self.search_page.goto(self.homepage)

            if self.hasSignIn:
                await self.__sign_in(self.sign_in(self.account["username"], self.account["password"]))
            
            for productName in self.productNames:
                await self.__search_product(productName)
                tasks = [self.asyncManager.start_all_queues(), self.__get_all_products_links()]
                await asyncio.gather(*tasks)
                # await self.__get_all_products_links()
        

    async def __sign_in(self, username, password):
        """Sign in to Amazon."""
        await PlaywrightUtils.wait_for_element(self.search_page, "#nav-link-accountList")
        await self.search_page.locator("#nav-link-accountList").click()

        # Enter email
        await PlaywrightUtils.wait_for_element(self.search_page, "#ap_email")
        await PlaywrightUtils.type_like_human(self.search_page, "#ap_email", username)
        await self.search_page.locator("#continue.a-button-input").click()

        # Enter password
        await PlaywrightUtils.wait_for_element(self.search_page, "#ap_password")
        await PlaywrightUtils.type_like_human(self.search_page, "#ap_password", password)
        await self.search_page.locator("#auth-signin-button").click()
        await PlaywrightUtils.wait_for_page_load(self.search_page)

    async def __search_product(self, productName):
        """Search for a product."""
        # if self.hasSignIn and not self.isNextProduct:
        #     page = await self.sign_in(self.account["username"], self.account["password"])
        # elif not self.hasSignIn and not self.isNextProduct:
        #     page = await self.init_environment()
        # else:
        #     page = await self.initialize_page(self.homepage)
        await PlaywrightUtils.wait_for_element(self.search_page, "#twotabsearchtextbox")
        await self.search_page.locator("#twotabsearchtextbox").fill("", timeout=15000)
        await PlaywrightUtils.type_like_human(self.search_page, "#twotabsearchtextbox", productName)
        await self.search_page.keyboard.press("Enter")
        await PlaywrightUtils.wait_for_page_load(self.search_page)

    async def __get_all_products_links(self):
        """Get all product links."""
        pageNo = 1
        countLink = 0
        while True:
            print("Crawling the next page...")
            await PlaywrightUtils.wait_for_element(self.search_page, "//div[contains(@class, 's-desktop-width-max')]")
            await PlaywrightUtils.scroll_to_bottom(self.search_page, delay=3)

            # Extract product links
            elems = self.search_page.locator("//span//a[@class='a-link-normal s-no-outline']")
            links = await elems.evaluate_all("elements => elements.map(e => e.href)")
            countLink += len(links)
            print(f"Collected {countLink} product links.")
            for link in links:
                await self.asyncManager.add_task(self.__scrape_html_source(link, str(uuid.uuid1())))
            # await self.asyncManager.start_all_queues()
            # Attempt to navigate to the next page
            
            nextBtn = await PlaywrightUtils.wait_for_element(self.search_page, "a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-button-accessibility.s-pagination-separator", attempts=3)
            if nextBtn is not None:
                await nextBtn.click()
                pageNo += 1
                print("Pressed next page")
            else:
                print("Reached the last page or an error occurred")
                break
        await self.search_page.close()

    async def __scrape_html_source(self, product_page, name):
        page = await self.initialize_page(self.main_context, product_page)
        attempts = 3
        # await PlaywrightUtils.wait_for_element(page, ".a-size-large.product-title-word-break", attempts=3)
        while attempts > 0:
            if await page.title() in ["503 - Service Unavailable Error", "Sorry! Something went wrong!", "Sorry! Something went wrong"]:
                await asyncio.sleep(2)
                await page.goto(product_page)
                attempts -= 1
            else:
                html = await page.content()
                minimized_html = await self.minimize_html(html)
                await PlaywrightUtils.scroll_to_bottom(page, delay=3)
                self.cloudManager.storage_client.upload_from_string(destination_path=os.path.join(self.config_values['bucket_name'], "raw-html", name),
                                                                    data=minimized_html)
                await asyncio.sleep(1)
                await page.close()
                break
        else:
            await page.close()
    
    @staticmethod
    async def minimize_html(pageContent):
        soup = BeautifulSoup(pageContent, "html.parser")

        # Remove scripts, styles, and comments
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Minify the HTML (remove extra spaces/newlines)
        minimized_html = ' '.join(soup.prettify().split())
        return minimized_html
        

    async def scrape_multiple_sources(self, productLinks):
        tasks = []
        for page_link in productLinks:
            # Pass the shared context to each task
            tasks.append(self.__scrape_html_source(page_link, str(uuid.uuid1())))
        # Run all tasks concurrently
        await tqdm.gather(*tasks)
        

class AmazonPyppetScraper(WebsitePyppetScraper):
    product_links = []

    def __init__(self, executablePath, product_name, account=dict(username=None, apple=None), homepage="https://amazon.com", headless=False, proxy=None):
        super().__init__(executablePath, headless, proxy)
        self.homepage = homepage
        self.account = account
        self.product_name = product_name

    async def sign_in(self, username, password) -> page.Page:
        # Click the account button
        await self.initialize_browser()
        page = await self.initialize_page(self.homepage)
        await PyppeteerUtils.wait_for_CSS_element(page, "#nav-link-accountList")
        await page.click("#nav-link-accountList")
        await PyppeteerUtils.wait_for_page_load(page)

        # Enter username
        await PyppeteerUtils.wait_for_CSS_element(page, "#ap_email")
        await PyppeteerUtils.type_like_human(page, "#ap_email", username, delay_range=(0.2, 0.5))
        await page.click("#continue")
        await PyppeteerUtils.wait_for_page_load(page)

        # Enter password
        await PyppeteerUtils.wait_for_CSS_element(page, "#ap_password")
        await PyppeteerUtils.type_like_human(page, "#ap_password", password, delay_range=(0.2, 0.5))
        await page.click("#auth-signin-button")
        await PyppeteerUtils.wait_for_page_load(page)
        return page
    
    async def search_product(self):
        page = await self.sign_in(self.account["username"], self.account["password"])
        await PyppeteerUtils.wait_for_CSS_element(page, "#twotabsearchtextbox")
        await page.evaluate("(selector) => document.querySelector(selector).value = ''", "#twotabsearchtextbox")
        print(f"Typing {self.product_name}")
        await PyppeteerUtils.type_like_human(page, "#twotabsearchtextbox", self.product_name, delay_range=(0.2, 0.5))
        await page.keyboard.press("Enter")
        return page

    async def get_all_products_links(self):
        page = await self.search_product()
        while True:
            # Wait for product listings
            await PyppeteerUtils.wait_for_XPATH_element(page, "//div[@class='s-desktop-width-max s-desktop-content s-opposite-dir s-wide-grid-style sg-row']", timeout=5000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

            # Collect product links
            elems = await page.xpath("//span//a[@class='a-link-normal s-no-outline']")
            for ele in elems:
                href = await page.evaluate("(element) => element.href", ele)
                self.product_links.append(href)

            # Try to navigate to the next page
            try:
                await PyppeteerUtils.wait_for_XPATH_element(page, "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator']")
                await page.click("//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator']")
                await asyncio.sleep(3)
            except Exception as e:
                print(f"Reached the last page or an error occurred: {e}")
                break
        print(self.product_links)
    
    async def activate_scraper(self):
        await self.get_all_products_links()
        await asyncio.sleep(3)
    









# # Get product details
# async def get_product_detail(browser, href):
#     page = await browser.newPage()
#     await page.goto(href)
#     await wait_for_page_load(page)

#     # Scrape product name
#     product_name_elem = await wait_for_element(page, "#productTitle")
#     product_name = await page.evaluate("(element) => element.textContent", product_name_elem)

#     # Scrape product price
#     price_elem = await wait_for_element(page, "//div[@id='corePriceDisplay_desktop_feature_div']//span[@class='aok-offscreen']")
#     price_raw = await page.evaluate("(element) => element.textContent", price_elem)
#     price = price_raw.split()
#     print("Product Name:", product_name)
#     print("Price:", price)

# # Main function
# async def main():
#     browser = await launch(headless=True)  # Launch browser
#     page = await browser.newPage()

#     # Example usage
#     url = "https://www.amazon.com"  # Update with the actual URL
#     username = "your_email@example.com"
#     password = "your_password"

#     await sign_in(browser, url, username, password)
#     await search_product(page, "laptop")
#     await get_all_products_links(page)

#     # Scrape details for the first product link
#     if product_links:
#         await get_product_detail(browser, product_links[0])

#     await browser.close()  # Close browser

# if __name__ == "__main__":
#     asyncio.run(main())


