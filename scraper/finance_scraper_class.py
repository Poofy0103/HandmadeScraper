from .web_scraper_class import WebsitePWrightScraper, PlaywrightBaseScraper
from common.playwright_utils import PlaywrightUtils
from playwright.async_api import Page, Locator, BrowserContext
import asyncio
# from common.asyncioManager import AsyncioManager
from common.utils.ggcloud import CloudManager
import threading
from bs4 import BeautifulSoup, Comment
from tqdm.asyncio import tqdm
import os
from common.config import read_config
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn
import pandas as pd
import json

class FinanceScraperClass(WebsitePWrightScraper):
    product_page = []
    isNextProduct = False
    condition = asyncio.Condition()
    cloudManager = CloudManager()
    # config_values = read_config()

    def __init__(self, productNames: list, homepage, timeRange, hasSignIn = False, account=dict(username=None, password=None), headless=False, proxy=None, maxQueueSize = 0, queuesNum = 2):
        super().__init__(headless, proxy)
        self.homepage = homepage
        self.account = account
        self.productNames = productNames
        self.hasSignIn = hasSignIn
        self.timeRange = timeRange
        # self.asyncManager = AsyncioManager(maxSize=maxQueueSize, queuesNum=queuesNum)

    async def scraping_driver(self):
        await self.initialize_browser()
        workers = [FinanceScraperWorker(self.main_context, self.homepage, productName, self.timeRange) for productName in self.productNames]
        tasks = [worker.scraping_task() for worker in workers]
        await asyncio.gather(*tasks)
        

class FinanceScraperWorker(PlaywrightBaseScraper):
    def __init__(self, main_context: BrowserContext, homepage: str, productName: str, timeRange: str):
        self.main_context = main_context
        self.homepage = homepage
        self.productName = productName
        self.timeRange = timeRange
        self.result = []

    async def scraping_task(self):
        self.page = await self.initialize_page(self.main_context, self.homepage)
        await self.__search_stock()
        await self.__iterate_multiple_stock_tables()
        with open(f"scrape_results/{self.productName}.json", "w+", encoding="utf-8") as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)
        print(pd.DataFrame.from_dict(self.result))
    
    async def __search_stock(self):
        """Search for a product."""
        search_stock_selector = "//div[@class='owner-inputSymbol']/input[@class='input-owner']"
        search_time_selector = "//div[@class='owner-date-exportFile']/div[@class='choseTime']/input"
        search_button_selector = "//div[@class='owner-find-export']/div[@class='owner-find']"
        submit_time_selector = "button.applyBtn.btn.btn-sm.btn-primary"

        search_stock_input = await PlaywrightUtils.wait_for_element(self.page, search_stock_selector)
        await search_stock_input.fill("", timeout=15000) 
        await PlaywrightUtils.type_like_human_v2(search_stock_input, self.productName)
        await asyncio.sleep(1)

        search_time_input = await PlaywrightUtils.wait_for_element(self.page, search_time_selector)
        await search_time_input.fill("", timeout=15000) 
        await PlaywrightUtils.type_like_human_v2(search_time_input, self.timeRange)
        await asyncio.sleep(1)

        submit_time_button = await PlaywrightUtils.wait_for_element(self.page, submit_time_selector)
        await submit_time_button.click()
        await asyncio.sleep(1)

        search_button_selector = await PlaywrightUtils.wait_for_element(self.page, search_button_selector)
        await search_button_selector.click()
        await asyncio.sleep(2)

    async def __iterate_multiple_stock_tables(self):
        current_page_index = 1
        #Find max page for iteration
        max_page_index = 1
        all_pages_list = await self.page.locator("//div[@id='wraper-content-paging']/div/p").all_text_contents()
        for i in all_pages_list:
            if int(i) > max_page_index:
                max_page_index = int(i)
            
        while current_page_index <= max_page_index:
            await self.__iterate_stock_table()
            await self.page.locator("//div[@onclick='ownerCDL.handleChangePage(ownerCDL.pageIndex + 1)']").click()
            current_page_index += 1
            await asyncio.sleep(1)

    async def __iterate_stock_table(self):
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
                    "close_price": all_close_prices[0],
                    "modified_close_price": all_close_prices[1] if len(all_close_prices)>1 else None,
                    "transaction_volume": all_transaction_volume[0]
                }
            )
            print(self.result)
    
