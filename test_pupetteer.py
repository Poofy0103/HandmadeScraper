import asyncio
import time
from pyppeteer import launch
async def scraper():
   browser =await launch({"headless": False, "executablePath": "chromedriver.exe"})
   page = await browser.newPage()
   await page.goto("amazon.com")
   time.sleep(100)
   await browser.close()

asyncio.run(scraper())