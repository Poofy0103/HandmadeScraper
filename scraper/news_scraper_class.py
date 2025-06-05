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
from datetime import datetime

class NewsScraperClass(WebsitePWrightScraper):
    product_page = []
    isNextProduct = False
    condition = asyncio.Condition()
    # cloudManager = CloudManager()

    def __init__(self, stockCodes: list[str], homepage: str, timeRange, hasSignIn = False, account=dict(username=None, password=None), headless=False, proxy=None, maxQueueSize = 0, queuesNum = 2):
        super().__init__(headless, proxy)
        self.homepage = homepage
        self.account = account
        self.stockCodes = stockCodes
        self.hasSignIn = hasSignIn
        self.timeRange = timeRange
        # self.asyncManager = AsyncioManager(maxSize=maxQueueSize, queuesNum=queuesNum)

    async def scraping_driver(self):
        await self.initialize_browser()
        workers = [NewsScraperWorker(self.main_context, self.homepage.format(stockCode.lower()), stockCode, self.timeRange) for stockCode in self.stockCodes]
        tasks = [worker.scraping_task() for worker in workers]
        await asyncio.gather(*tasks)
        

class NewsScraperWorker(PlaywrightBaseScraper):
    config_values = read_config()
    def __init__(self, main_context: BrowserContext, homepage: str, stockCode: str, timeRange: str):
        self.main_context = main_context
        self.homepage = homepage
        self.stockCode = stockCode
        self.startTime = datetime.strptime(timeRange.split('-')[0].strip(), "%d/%m/%Y").year
        self.endTime = datetime.strptime(timeRange.split('-')[1].strip(), "%d/%m/%Y").year
        self.db = FinanceDatabase(self.config_values['finance_db_username'],
                     self.config_values['finance_db_password'],
                     self.config_values['finance_db_server'],
                     self.config_values['finance_db_port'],
                     self.config_values['finance_db_schema'])
        self.result = []

    async def scraping_task(self):
        self.page = await self.initialize_page(self.main_context, self.homepage)
        await self.__iterate_multiple_stock_tables()
        with open(f"scrape_results/news/{self.stockCode}.json", "w+", encoding="utf-8") as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)
        print(pd.DataFrame.from_dict(self.result))
        self.db.submit_news_data(self.stockCode, self.result)
        self.db.close_connection()

    async def __iterate_multiple_stock_tables(self):
        print(f"Start crawling stock price data for stock {self.stockCode}")
        #Find max page for iteration
        self.currentYear = self.endTime
        
        while self.currentYear >= self.startTime:
            print(f"[{self.stockCode}]: Currently crawling data for year: {self.currentYear}")
            await self.__iterate_stock_table()
            await self.page.locator("//span[@id='spanNext']").click()
            await asyncio.sleep(0.5)

    async def __iterate_stock_table(self):
        tableSelector = "//div[@class='tintucsukien']/div/div/div/ul"
        await PlaywrightUtils.wait_for_element(self.page, tableSelector)
        table: Locator = self.page.locator(tableSelector)
        articleRows: Locator = table.locator("li")
        await self.__extract_row(articleRows)

    async def __extract_row(self, rows: Locator):
        for row in await rows.all():
            date: Locator = await row.locator("span").text_content()
            crawled_year = datetime.strptime(date[0:10], "%d/%m/%Y").year
            a_element: Locator = row.locator("a")
            title = await a_element.text_content()
            url_link = "https://cafef.vn"+ await a_element.get_attribute("href")
            self.result.append(
                {
                    "date": date[0:10],
                    "title": title,
                    "url_link": url_link
                }
            )
            if crawled_year < self.currentYear:
                self.currentYear = crawled_year
