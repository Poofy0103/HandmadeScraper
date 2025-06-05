from .web_scraper_class import WebsitePWrightScraper, PlaywrightBaseScraper
from common.playwright_utils import PlaywrightUtils
from playwright.async_api import Page, Locator, BrowserContext
import asyncio
# from common.asyncioManager import AsyncioManager
import threading
from bs4 import BeautifulSoup, Comment
from tqdm.asyncio import tqdm
import os
from common.config import read_config
from common.db import FinanceDatabase
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
    config_values = read_config()
    def __init__(self, main_context: BrowserContext, homepage: str, place: str, timeRange: str):
        self.main_context = main_context
        self.homepage = homepage
        self.place = place
        self.timeRange = timeRange
        self.db = FinanceDatabase(self.config_values['finance_db_username'],
                     self.config_values['finance_db_password'],
                     self.config_values['finance_db_server'],
                     self.config_values['finance_db_port'],
                     self.config_values['finance_db_schema'])
        self.result = []

    async def scraping_task(self):
        self.page = await self.initialize_page(self.main_context, self.homepage)
        await self.__search_place()
        await self.__scan_matches()
        # await self.__iterate_multiple_place_tables()
        # with open(f"scrape_results/transaction/{self.place}.json", "w+", encoding="utf-8") as f:
        #     json.dump(self.result, f, ensure_ascii=False, indent=4)
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

    async def __iterate_multiple_place_tables(self):
        print(f"Start crawling place price data for place {self.place}")
        current_page_index = 1
        #Find max page for iteration
        max_page_index = 1
        all_pages_list = await self.page.locator("//div[@id='wraper-content-paging']/div/p").all_text_contents()
        for i in all_pages_list:
            if int(i) > max_page_index:
                max_page_index = int(i)
        
        with tqdm(total = max_page_index - current_page_index) as pbar:
            while current_page_index <= max_page_index:
                await self.__iterate_place_table()
                await self.page.locator("//div[@onclick='ownerCDL.handleChangePage(ownerCDL.pageIndex + 1)']").click()
                current_page_index += 1
                pbar.update(1)
                await asyncio.sleep(0.5)

    async def __iterate_place_table(self):
        table_selector = "//tbody[@class='render-table-owner']"
        await PlaywrightUtils.wait_for_element(self.page, table_selector)
        table: Locator = self.page.locator(table_selector)
        oddRows: Locator = table.locator("tr.oddOwner")
        await self.__extract_row(oddRows)

        #Sometimes page only has one row
        if await self.page.wait_for_selector("tr.evenOwner", timeout=1000):
            evenRows: Locator = table.locator("tr.evenOwner")
            await self.__extract_row(evenRows)
        

    async def __extract_row(self, rows: Locator):
        for row in await rows.all():
            all_close_prices = await row.locator("td.owner_priceClose").all_text_contents()
            all_transaction_volume = await row.locator("td.owner_gd_td").all_text_contents()
            self.result.append(
                {
                    "date": await row.locator("td.owner_time").text_content(),
                    "place_code": self.placeCode,
                    "close_price": float(all_close_prices[0].replace(",","")) if all_close_prices[0] != "--" else None,
                    "modified_close_price": float(all_close_prices[1].replace(",","")) if len(all_close_prices) > 1 and all_close_prices[1] != "--" else None,
                    "transaction_volume": float(all_transaction_volume[0].replace(",",""))
                }
            )
    
