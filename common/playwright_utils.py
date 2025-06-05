import asyncio
import random
import re
from playwright.async_api import async_playwright, Page, Browser, ElementHandle

class PlaywrightUtils:
    @staticmethod
    # Simulate human-like typing
    async def type_like_human(page: Page, selector: str, text: str, delay_range=(100, 300)):
        for char in text:
            await page.locator(selector).type(char, delay=random.uniform(*delay_range))
    
    @staticmethod
    # Simulate human-like typing
    async def type_like_human_v2(element: ElementHandle, text: str, delay_range=(100, 300)):
        for char in text:
            await element.type(char, delay=random.uniform(*delay_range))

    @staticmethod
    # Wait for an element to appear on the page
    async def wait_for_element(page: Page, selector, timeout=10000, attempts = 3) -> ElementHandle:
        """Wait for an element to appear on the page."""
        while attempts > 1:
            try:
                ele = await page.wait_for_selector(selector, timeout=timeout)
                return ele
            except Exception as e:
                print(f"Cannot find {selector}. Reload and try again!!")
                await page.reload()
                attempts -= 1
        else:
            return None
    
    async def wait_for_element_no_attempt(page: Page, selector, timeout=10000) -> ElementHandle:
        """Wait for an element to appear on the page."""
        try:
            ele = await page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False

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
