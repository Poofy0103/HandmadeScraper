import asyncio
import random
import re
from playwright.async_api import async_playwright, Page, Browser

class PlaywrightUtils:
    @staticmethod
    # Simulate human-like typing
    async def type_like_human(page: Page, selector: str, text: str, delay_range=(100, 300)):
        for char in text:
            await page.locator(selector).type(char, delay=random.uniform(*delay_range))

    @staticmethod
    # Wait for an element to appear on the page
    async def wait_for_element(page: Page, selector, timeout=10000, attempts = 3):
        """Wait for an element to appear on the page."""
        foundit = False
        while attempts > 0 and foundit != True:
            try:
                ele = await page.wait_for_selector(selector, timeout=timeout)
                await asyncio.sleep(3)
                return ele
            except Exception as e:
                await page.reload()
                attempts -= 1
        else:
            print(f"Attempts are exceeded")

    @staticmethod
    # Wait for the full page to load
    async def wait_for_page_load(page: Page):
        """Wait for the full page to load."""
        await page.wait_for_load_state("load")

    @staticmethod
    # Scroll to the bottom of the page
    async def scroll_to_bottom(page: Page, delay=3):
        """Scroll to the bottom of the page."""
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(delay)
