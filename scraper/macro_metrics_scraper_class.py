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

class MacroMetricsScraperClass(WebsitePWrightScraper):
    product_page = []
    isNextProduct = False
    condition = asyncio.Condition()
    # cloudManager = CloudManager()
    urlMap = {
        "dailyData": {
            "exchangerate-interest": {
                "urlLink": "https://finance.vietstock.vn/du-lieu-vi-mo/53-64/ty-gia-lai-suat.htm",
                "crawledIndex": 1
            }
        },
        "monthlyData": {
            "cpi": {
                "urlLink": "https://finance.vietstock.vn/du-lieu-vi-mo/52/cpi.htm",
                "crawledIndex": 0
            },
            "sxcn": {
                "urlLink": "https://finance.vietstock.vn/du-lieu-vi-mo/46/san-xuat-cong-nghiep.htm",
                "crawledIndex": 1
            },
            "m2": {
                "urlLink": "https://finance.vietstock.vn/du-lieu-vi-mo/51/tin-dung.htm",
                "crawledIndex": 1
            }
        }
    }

    def __init__(self, homepage: str, timeRange, hasSignIn = False, account=dict(username=None, password=None), headless=False, proxy=None, maxQueueSize = 0, queuesNum = 2):
        super().__init__(headless, proxy)
        self.homepage = homepage
        self.account = account
        self.hasSignIn = hasSignIn
        self.timeRange = timeRange
        # self.asyncManager = AsyncioManager(maxSize=maxQueueSize, queuesNum=queuesNum)

    async def scraping_driver(self):
        await self.initialize_browser()
        workersMonthly = [MacroMetricsScraperWorker(self.main_context, details["urlLink"], metric, self.timeRange, details["crawledIndex"]) for metric, details in self.urlMap["monthlyData"].items()]
        workersDaily = [MacroMetricsScraperWorker(self.main_context, details["urlLink"], metric, self.timeRange, details["crawledIndex"]) for metric, details in self.urlMap["dailyData"].items()]
        tasks = []
        # tasks.extend([worker.scraping_monthly_data_task() for worker in workersMonthly])
        tasks.extend([worker.scraping_daily_data_task() for worker in workersDaily])
        for task in tasks:
            await task
        

class MacroMetricsScraperWorker(PlaywrightBaseScraper):
    config_values = read_config()
    def __init__(self, main_context: BrowserContext, urlLink: str, metric: str, timeRange: str, crawledIndex: int):
        self.main_context = main_context
        self.urlLink = urlLink
        self.metric = metric
        self.timeRange = timeRange
        self.crawledIndex = crawledIndex
        self.startTime = datetime.strptime(timeRange.split('-')[0].strip(), "%d/%m/%Y")
        self.endTime = datetime.strptime(timeRange.split('-')[1].strip(), "%d/%m/%Y")
        self.db = FinanceDatabase(self.config_values['finance_db_username'],
                     self.config_values['finance_db_password'],
                     self.config_values['finance_db_server'],
                     self.config_values['finance_db_port'],
                     self.config_values['finance_db_schema'])
        self.result = []

    async def scraping_daily_data_task(self):
        self.page = await self.initialize_page(self.main_context, self.urlLink)
        await self.page.locator("//div[contains(@class, 'btn-group')]/a[contains(@class, 'btn-default')]").click()
        await asyncio.sleep(2)
        # await self.__select_day_data('01/01/2019', '31/12/2021')
        # await self.__iterate_daily_metric_table(3)
        await self.__select_day_data('01/01/2022', '31/12/2024')
        await self.__iterate_daily_metric_table(3)
        with open(f"scrape_results/macro_metrics/{self.metric}_interest.json", "w+", encoding="utf-8") as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)

        # await self.page.locator("//div[contains(@class, 'btn-group')]/a[contains(@class, 'btn-default')]").click()

        # await asyncio.sleep(0.5)
        # await self.__select_day_data(self.timeRange.split('-')[0].strip(), self.timeRange.split('-')[1].strip())
        # await self.__iterate_daily_metric_table(1)
        # with open(f"scrape_results/macro_metrics/{self.metric}_exchange.json", "w+", encoding="utf-8") as f:
        #     json.dump(self.result, f, ensure_ascii=False, indent=4)

        print(pd.DataFrame.from_dict(self.result))
    
    async def scraping_monthly_data_task(self):
        self.page = await self.initialize_page(self.main_context, self.urlLink)
        await asyncio.sleep(0.5)
        await self.__select_month_data(str(self.startTime.month), str(self.startTime.year), str(self.endTime.month), str(self.endTime.year))
        await asyncio.sleep(2)
        await self.__iterate_monthly_metric_table()
        with open(f"scrape_results/macro_metrics/{self.metric}.json", "w+", encoding="utf-8") as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)
        print(pd.DataFrame.from_dict(self.result))

    async def __select_month_data(self, fromMonth, fromYear, toMonth, toYear):
        fromMonthSelector = "//select[@name='from']"
        fromYearSelector = "//select[@name='fromYear']"
        toMonthSelector = "//select[@name='to']"
        toYearSelector = "//select[@name='toYear']"
        submitButtonSelector = "//div[contains(@class, 'form-inline')]/button"

        await PlaywrightUtils.wait_for_element(self.page, fromMonthSelector)
        await PlaywrightUtils.wait_for_element(self.page, fromYearSelector)
        await PlaywrightUtils.wait_for_element(self.page, toMonthSelector)
        await PlaywrightUtils.wait_for_element(self.page, toYearSelector)
        await PlaywrightUtils.wait_for_element(self.page, submitButtonSelector)
        await self.page.locator(fromYearSelector).select_option(fromYear)
        await self.page.locator(fromMonthSelector).select_option(fromMonth)
        await self.page.locator(toYearSelector).select_option(toYear)
        await self.page.locator(toMonthSelector).select_option(toMonth)
        await self.page.locator(submitButtonSelector).click()
        await asyncio.sleep(1)
    
    async def __select_day_data(self, fromDate, toDate):
        fromDateSelector = "//input[@name='fromDate']"
        toDateSelector = "//input[@name='toDate']"
        buttonSelector = "button.btn.bg.m-l"

        await PlaywrightUtils.wait_for_element(self.page, fromDateSelector)
        await PlaywrightUtils.wait_for_element(self.page, toDateSelector)
        await PlaywrightUtils.wait_for_element(self.page, buttonSelector)
        fromDateInput = self.page.locator(fromDateSelector)
        await fromDateInput.fill("", timeout=15000)
        await PlaywrightUtils.type_like_human_v2(fromDateInput, fromDate)

        fromDateInput = self.page.locator(toDateSelector)
        await fromDateInput.fill("", timeout=15000)
        await PlaywrightUtils.type_like_human_v2(fromDateInput, toDate)

        await self.page.locator(buttonSelector).click()
        await asyncio.sleep(1)

    async def __iterate_monthly_metric_table(self):
        headerSelector = "//div[contains(@class, 'table-responsive')]/table/thead/tr/th[@class='text-right']"
        bodySelector = "//div[contains(@class, 'table-responsive')]/table/tbody/tr"

        await PlaywrightUtils.wait_for_element(self.page, headerSelector)
        headerElements = await self.page.locator(headerSelector).all()
        bodyElements = await self.page.locator(bodySelector).all()
        
        validBodyElements = bodyElements[self.crawledIndex]
        tdBodyElements = await validBodyElements.locator("//td[@class='text-right']").all()

        for index, ele in enumerate(headerElements):
            date = await ele.text_content()
            metric = await tdBodyElements[index].text_content()
            self.result.append(
                {
                    "date": date.replace("Tháng ", ""),
                    self.metric: float(metric.replace(",", ""))
                }
            )
        await asyncio.sleep(1)
    
    async def __iterate_daily_metric_table(self, crawledIndex):
        headerSelector = "//div[contains(@class, 'table-responsive')]/table/thead/tr/th[@class='text-right']"
        bodySelector = "//div[contains(@class, 'table-responsive')]/table/tbody/tr"
        await asyncio.sleep(1)

        await PlaywrightUtils.wait_for_element(self.page, headerSelector)
        headerElements = await self.page.locator(headerSelector).all()
        bodyElements = await self.page.locator(bodySelector).all()
        
        validBodyElements = bodyElements[crawledIndex]
        tdBodyElements = await validBodyElements.locator("//td[@class='text-right']").all()

        for index, ele in enumerate(headerElements):
            date = await ele.text_content()
            metric = await tdBodyElements[index].text_content()
            self.result.append(
                {
                    "date": date.replace("Tháng ", ""),
                    self.metric: float(metric.replace(",", ""))
                }
            )
        
        await asyncio.sleep(1)