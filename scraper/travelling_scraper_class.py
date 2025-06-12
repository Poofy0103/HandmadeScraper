from .web_scraper_class import WebsitePWrightScraper, PlaywrightBaseScraper
from common.pyppeteer_utils import PyppeteerUtils
from common.playwright_utils import PlaywrightUtils
from playwright.async_api import Page, BrowserContext, Locator
import asyncio
from pyppeteer import launch, browser, page
import uuid
from common.asyncioManager import AsyncioManager
# from common.utils.ggcloud import CloudManager
import threading
from bs4 import BeautifulSoup, Comment
from tqdm.asyncio import tqdm
import os
import json
from common.config import read_config
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn
import aiofiles
import json



class TravellingScraperClass(WebsitePWrightScraper):
    product_page = []
    isNextProduct = False
    condition = asyncio.Condition()
    # cloudManager = CloudManager()
    # config_values = read_config()

    def __init__(self, productNames: list, homepage, scroll_page_attempt: int, hasSignIn = False, account=dict(username=None, password=None), headless=False, proxy=None, maxQueueSize = 0, queuesNum = 2):
        super().__init__(headless, proxy)
        self.homepage = homepage
        self.account = account
        self.productNames = productNames
        self.hasSignIn = hasSignIn
        self.scroll_page_attempt = scroll_page_attempt
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
            workers = [TravellingScraperWorker(self.main_context, self.homepage, place, self.asyncManager, self.scroll_page_attempt) for place in self.productNames]
            tasks = [worker.scraping_task() for worker in workers]
            tasks.append(self.asyncManager.start_all_queues())
            await asyncio.gather(*tasks)

            # for productName in self.productNames:
            #     await self.__search_place(productName)
            #     tasks = [self.asyncManager.start_all_queues(), self.__get_all_products_links()]
            #     await asyncio.gather(*tasks)
            #     # await self.__get_all_products_links()

        


class TravellingScraperWorker(PlaywrightBaseScraper):
    # config_values = read_config()
    def __init__(self, main_context: BrowserContext, homepage: str, place: str, asyncManager: AsyncioManager, scroll_page_attempt: int):
        self.main_context = main_context
        self.homepage = homepage
        self.place = place
        self.asyncManager = asyncManager
        self.scroll_page_attempt = scroll_page_attempt
        self.result = []

    async def scraping_task(self):
        self.page = await self.initialize_page(self.main_context, self.homepage)
        # threading.Thread(target=self.__close_dialog, args=(), daemon=True).start()
        await self.__search_place()
        links = await self.__scan_matches()
        for link in links:
            await self.asyncManager.add_task(self.__scrape_html_source(link))
        
        # print(pd.DataFrame.from_dict(self.result))
        # self.db.submit_placeprice_data(self.place, self.result)
        # self.db.close_connection()
    
    async def __search_place(self):
        """Search for a product."""
        print(f"Searching for place {self.place}")
        search_place_selector = "//div[@class='hero-banner-searchbox ']/div/form/div/div/div/div/div/div/div/input"
        submit_time_selector = "button.de576f5064.b46cd7aad7.ced67027e5.dda427e6b5.e4f9ca4b0c.ca8e0b9533.cfd71fb584.a9d40b8d51"

        search_place_input = await PlaywrightUtils.wait_for_element(self.page, search_place_selector)
        await self.page.locator(search_place_selector).fill("", timeout=15000) 
        await PlaywrightUtils.type_like_human_v2(search_place_input, self.place)
        await asyncio.sleep(0.5)
        await self.page.locator(submit_time_selector).click()
        await asyncio.sleep(5)
    
    async def __scan_matches(self):
        load_more_button_selector = "button.de576f5064.b46cd7aad7.d0a01e3d83.dda427e6b5.bbf83acb81.a0ddd706cc"
        matches_list_selector = "//div[@role='list']/div[@role='listitem']/div/div/div/div/div/div/div/div/h3/a"
        while self.scroll_page_attempt > 0:
            await PlaywrightUtils.scroll_to_bottom(self.page, delay=5)
            if await PlaywrightUtils.wait_for_element_no_attempt(self.page, load_more_button_selector, 3000):
                await self.page.locator(load_more_button_selector).click()
            self.scroll_page_attempt -= 1
        matches_list_element = self.page.locator(matches_list_selector)
        links = await matches_list_element.evaluate_all("elements => elements.map(e => e.href)")
        return links
    
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
        

    async def __scrape_html_source(self, product_page):
        page = await self.initialize_page(self.main_context, product_page)
        await asyncio.sleep(1)
        # html = await page.content()
        # minimized_html = await self.minimize_html(html)
        # await self.parse_booking_html(minimized_html)
        place_name_selector = "//div[@id='wrap-hotelpage-top']/div/div/div/h2"
        address_selector = "//div[@data-testid='PropertyHeaderAddressDesktop-wrapper']/div[@class='b6937ecb12']/span[@class='a297f43545']/button/div"
        facilities_selector = "//div[@data-testid='property-most-popular-facilities-wrapper']/div/ul"
        reviews_scorecard_selector = "//div[@id='js--hp-gallery-scorecard']"
        overall_review_selector = "//div[@data-testid='review-score-right-component']/div[contains(@class, 'f63b14ab7a')]"
        review_card_selector = "//div[@data-testid='review-card']/div/div/div[@aria-label='Review']"
        next_button_selector = "//div[contains(@class,'d8026226a7')]/button[@aria-label='Next page']"

        place_name = await page.locator(place_name_selector).text_content()
        address = await page.locator(address_selector).text_content()
        facilities = None
        overall_review = None
        try:
            raw_facilities = await page.locator(facilities_selector).all_text_contents()
            facilities = ",".join(raw_facilities)
        except:
            print('No facilities')

        try:
            overall_review = await page.locator(overall_review_selector).text_content()
            overall_review = float(overall_review)
        except:
            print('No facilities')
        
        attempts = 5
        comment_result = []
        try:
            if await PlaywrightUtils.wait_for_element_no_attempt(page, reviews_scorecard_selector, timeout=15000):
                await page.locator(reviews_scorecard_selector).click()
                await asyncio.sleep(3)
                await page.locator("//div[@role='dialog']/div/div[@class='c1cb99b7ca']").evaluate("e => e.scrollTop += 1200")
                while attempts > 0:
                    try: 
                        review_cards: Locator = page.locator(review_card_selector)
                    except:
                        print('No reviews')
                        break
                    for card in await review_cards.all():
                        comment_title_locator: Locator = card.locator("//h4[@data-testid='review-title']")
                        comment_title = await comment_title_locator.text_content(timeout=4000)
                        comment_score_locator: Locator = card.locator("//div[@data-testid='review-score']/div/div[@aria-hidden='true']")
                        comment_score = await comment_score_locator.text_content(timeout=4000)
                        positive_comment = None
                        negative_comment = None
                        
                        try:
                            positive_comment_locator = card.locator("//div[@data-testid='review-positive-text']/div/div[@class='ea9fc823c1']/div/span")
                            positive_comment = await positive_comment_locator.text_content(timeout=4000)
                        except Exception as e:
                            print(f'No pos comment: {e}')
                        
                        try:
                            negative_comment_locator = card.locator("//div[@data-testid='review-negative-text']/div/div[@class='ea9fc823c1']/div/span")
                            negative_comment = await negative_comment_locator.text_content(timeout=4000)
                        except:
                            print('No pos comment')
                        comment_result.append(
                            {
                                "comment_title": comment_title,
                                "comment_score": comment_score,
                                "positive_comment": positive_comment,
                                "negative_comment": negative_comment
                            }
                        )
                    await page.locator(next_button_selector).click()
                    attempts -= 1
                    await page.locator("//div[@role='dialog']/div/div[@class='c1cb99b7ca']").evaluate("e => e.scrollTop += 1200")
        finally:
            await page.close()
            self.result.append(
                    {
                        "place_name": place_name,
                        "address": address,
                        "facilities": facilities,
                        "overall_review": overall_review,
                        "comments": comment_result
                    }
                )
            async with aiofiles.open(f"scrape_results/{self.place}.json", "w", encoding="utf-8") as f:
                await f.write(json.dumps(self.result, ensure_ascii=False, indent=4))
    
    async def parse_booking_html(self, html, place_name):
        soup = BeautifulSoup(html, "html.parser")

        # Extract place name
        place_name_tag = soup.select_one("div#wrap-hotelpage-top h2")
        place_name = place_name_tag.get_text(strip=True) if place_name_tag else None

        # Extract address
        address_tag = soup.select_one("div[data-testid='PropertyHeaderAddressDesktop-wrapper'] span.a297f43545 button div")
        address = address_tag.get_text(strip=True) if address_tag else None

        # Extract facilities
        facilities_list = []
        facilities_container = soup.select_one("div[data-testid='property-most-popular-facilities-wrapper'] ul")
        if facilities_container:
            facilities_list = [li.get_text(strip=True) for li in facilities_container.find_all("li")]
        facilities = ", ".join(facilities_list) if facilities_list else None

        # Extract overall review score
        overall_review_tag = soup.select_one("div[data-testid='review-score-right-component'] div.f63b14ab7a")
        overall_review = None
        if overall_review_tag:
            try:
                overall_review = float(overall_review_tag.get_text(strip=True))
            except ValueError:
                pass

        # Extract reviews
        comment_result = []
        review_cards = soup.select("div[data-testid='review-card'] div[aria-label='Review']")
        for card in review_cards:
            comment_title = card.select_one("h4[data-testid='review-title']")
            comment_score = card.select_one("div[data-testid='review-score'] div[aria-hidden='true']")
            positive_comment = card.select_one("div[data-testid='review-positive-text'] div.ea9fc823c1 span")
            negative_comment = card.select_one("div[data-testid='review-negative-text'] div.ea9fc823c1 span")

            comment_result.append({
                "comment_title": comment_title.get_text(strip=True) if comment_title else None,
                "comment_score": comment_score.get_text(strip=True) if comment_score else None,
                "positive_comment": positive_comment.get_text(strip=True) if positive_comment else None,
                "negative_comment": negative_comment.get_text(strip=True) if negative_comment else None
            })

        # Save result
        self.result.append(
            {
            "place_name": place_name,
            "address": address,
            "facilities": facilities,
            "overall_review": overall_review,
            "comments": comment_result
            }
        )