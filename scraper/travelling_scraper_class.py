from .web_scraper_class import WebsitePWrightScraper, PlaywrightBaseScraper
from common.playwright_utils import PlaywrightUtils
from playwright.async_api import Page, Locator, BrowserContext
import asyncio
# from common.asyncioManager import AsyncioManager
import threading
from bs4 import BeautifulSoup, Comment
from tqdm.asyncio import tqdm
import os
import pandas as pd
import json

class TravellingScraperClassCopy(WebsitePWrightScraper):
    product_page = []
    isNextProduct = False
    condition = asyncio.Condition()
    # cloudManager = CloudManager()

    def __init__(self, places: list, homepage, timeRange, hasSignIn = False, account=dict(username=None, password=None), headless=False, proxy=None, maxQueueSize = 0, queuesNum = 2):
        super().__init__(headless, proxy)
        self.homepage = homepage
        self.account = account
        self.places = places
        self.hasSignIn = hasSignIn
        self.timeRange = timeRange
        # self.asyncManager = AsyncioManager(maxSize=maxQueueSize, queuesNum=queuesNum)

    async def scraping_driver(self):
        await self.initialize_browser()
        workers = [TravellingScraperWorker(self.main_context, self.homepage, place, self.timeRange) for place in self.places]
        tasks = [worker.scraping_task() for worker in workers]
        await asyncio.gather(*tasks)
        

class TravellingScraperWorker(PlaywrightBaseScraper):
    def __init__(self, main_context: BrowserContext, homepage: str, place: str, timeRange: str):
        self.main_context = main_context
        self.homepage = homepage
        self.place = place
        self.timeRange = timeRange
        self.result = []

    async def scraping_task(self):
        self.page = await self.initialize_page(self.main_context, self.homepage)
        await self.__search_place()
        links = await self.__scan_matches()
        for link in links:
            await self.__scrape_html_source(link)
        # await self.__iterate_multiple_place_tables()
        with open(f"scrape_results/transaction/{self.place}.json", "w+", encoding="utf-8") as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)
        # async with aiofiles.open(f"scrape_results/{self.place}_{str(uuid.uuid1())}.json", "w", encoding="utf-8") as f:
        #     await f.write(json.dumps(self.result, ensure_ascii=False, indent=4))
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
        attempts = 5
        while attempts > 0:
            await PlaywrightUtils.scroll_to_bottom(self.page, delay=5)
            if await PlaywrightUtils.wait_for_element_no_attempt(self.page, load_more_button_selector, 3000):
                await self.page.locator(load_more_button_selector).click()
            attempts -= 1
        matches_list_element = self.page.locator(matches_list_selector)
        links = await matches_list_element.evaluate_all("elements => elements.map(e => e.href)")
        return links

    async def __scrape_html_source(self, product_page):
        page = await self.initialize_page(self.main_context, product_page)
        await asyncio.sleep(1)
        place_name_selector = "//div[@id='wrap-hotelpage-top']/div/div/div/h2"
        address_selector = "//div[@data-testid='PropertyHeaderAddressDesktop-wrapper']/div/span/button/div"
        facilities_selector = "//div[@data-testid='property-most-popular-facilities-wrapper']/div/ul"
        reviews_scorecard_selector = "//div[@id='js--hp-gallery-scorecard']"
        overall_review_selector = "//div[@data-testid='review-score-right-component']/div[contains(@class, 'f63b14ab7a')]"
        review_card_selector = "//div[@data-testid='review-card']/div/div/div[@aria-label='Review']"
        next_button_selector = "button.de576f5064.b46cd7aad7.e26a59bb37.c295306d66.c7a901b0e7.aaf9b6e287.fe5e267e55"

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
        
        attempts = 1
        comment_result = []
        try:
            if await PlaywrightUtils.wait_for_element_no_attempt(page, reviews_scorecard_selector, timeout=5000):
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
                        comment_title = await comment_title_locator.text_content()
                        comment_score_locator: Locator = card.locator("//div[@data-testid='review-score']/div/div[@aria-hidden='true']")
                        comment_score = await comment_score_locator.text_content()
                        positive_comment = None
                        negative_comment = None
                        try:
                            positive_comment_locator = page.locator("//div[@data-testid='review-positive-text']/div/div[@class='ea9fc823c1']/span")
                            positive_comment = await positive_comment_locator.text_content()
                        except:
                            print('No pos comment')
                        
                        try:
                            negative_comment_locator = page.locator("//div[@data-testid='review-negative-text']/div/div[@class='ea9fc823c1']/span")
                            negative_comment = await negative_comment_locator.text_content()
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
                        print(comment_result)
                    await page.locator(next_button_selector).click()
                    attempts -= 1
                    await page.locator("//div[@role='dialog']/div/div[@class='c1cb99b7ca']").evaluate("e => e.scrollTop += 100")
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
            print(self.result)
    
