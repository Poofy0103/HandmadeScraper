import asyncio
import random
import re
from pyppeteer import launch, browser, page

class PyppeteerUtils:
    @staticmethod
    # Simulate human-like typing
    async def type_like_human(page: page.Page, selector: str, text: str, delay_range=(0.1, 0.3)):
        for char in text:
            await page.type(selector, char)
            await asyncio.sleep(random.uniform(*delay_range))  # Random delay between key presses

    @staticmethod
    # Wait for an element to appear on the page
    async def wait_for_CSS_element(page: page.Page, selector: str, timeout=10000, attempts = 3):
        foundit = False
        while attempts > 0 and foundit != True:
            try:
                await page.waitForSelector(selector, {"timeout": timeout})
                print("Wait complete with detected objects")
                foundit = True
            except Exception as e:
                await page.reload()
                attempts -= 1
                # raise Exception(f"Wait timed out: {e}")
        
    @staticmethod
    # Wait for an element to appear on the page
    async def wait_for_XPATH_element(page: page.Page, xpath: str, timeout=10000, attempts = 3):
        foundit = False
        while attempts > 0 and foundit != True:
            try:
                await page.waitForXPath(xpath, {"timeout": timeout})
                print("Wait complete with detected objects")
                foundit = True
            except Exception as e:
                await page.reload()
                attempts -= 1
                # raise Exception(f"Wait timed out: {e}")

    @staticmethod
    # Wait for the full page to load
    async def wait_for_page_load(page: page.Page, timeout=30000):
        try:
            await page.waitForFunction(
                'document.readyState === "complete"', {"timeout": timeout}
            )
            print("Wait complete with full page loaded")
        except Exception as e:
            raise Exception(f"Wait timed out: {e}")

    @staticmethod
    # Scroll to the bottom of the page
    async def scroll_to_bottom(page: page.Page, delay=3):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(delay)  # Allow time for content to load
