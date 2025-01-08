import asyncio
import time
import seleniumwire.undetected_chromedriver as uc
from seleniumwire.webdriver import ChromeOptions
from pyppeteer import launch, browser, page
from pyppeteer_stealth import stealth
from playwright.async_api import async_playwright, Page, BrowserContext

class PlaywrightBaseScraper:
    browser = None
    main_context = None
    def __init__(self, headless=False, proxy=None):
        self.headless = headless
        self.proxy = proxy

    async def open_browser_session(self):
        """Open a browser session/context with BrowserContext"""
        session = await self.browser.new_context()
        return session
        
    async def initialize_browser(self):
        """Initialize a browser which can do tasks asynchronously"""
        playwright_context = await async_playwright().start()
        if self.proxy is not None:
            self.browser = await playwright_context.chromium.launch(headless=self.headless, proxy=self.proxy)
            # proxy = ({
            #   "server": "http://myproxy.com:3128",
            #   "username": "usr",
            #   "password": "pwd"
            # }
        else:
            self.browser = await playwright_context.chromium.launch(headless=self.headless)
        self.main_context = await self.open_browser_session()
        
    async def initialize_page(self, context: BrowserContext, url) -> Page:
        page = await context.new_page()
        await page.goto(url)
        return page

    async def close_browser(self):
        await self.browser.close()

class PyppeteerBaseScraper:
    def __init__(self, executablePath, headless=False, proxy=None):
        self.browser = None
        self.headless = headless
        self.executablePath = executablePath
        self.proxy = proxy
        
    async def initialize_browser(self):
        if self.proxy is not None:
            self.browser = await launch({"headless": self.headless, "executablePath": self.executablePath, "args": [f'--proxy-server={self.proxy}']})
            # await self.browser.authenticate({
            #     'username': username,
            #     'password': password
            # })
        else:
            self.browser = await launch({"headless": self.headless, "executablePath": self.executablePath, "defaultViewport": {"width": 1920, "height": 1080}})

    async def initialize_page(self, url) -> page.Page:
        page = await self.browser.newPage()
        await stealth(page, disabled_evasions=['chrome_app',
                                                'chrome_runtime',
                                                'iframe_content_window',
                                                'media_codecs',
                                                'sourceurl',
                                                'navigator_hardware_concurrency',
                                                'navigator_languages',
                                                'navigator_permissions',
                                                'navigator_plugins',
                                                'navigator_vendor',
                                                'navigator_webdriver',
                                                'user_agent_override',
                                                'webgl_vendor',
                                                'window_outerdimensions'])
        await page.goto(url)
        return page

    async def close_browser(self):
        await self.browser.close()


class SeleniumBaseScraper:
    def __init__(self, headless=False, proxy=None):
        self.options = ChromeOptions()
        self.selenium_options = dict()
        if headless:
            self.options.add_argument("--headless=new")
        if proxy:
            self.selenium_options['proxy'] = {'http': proxy, 'https': proxy}
        self.options.add_argument("--window-size=1280,800")
        self.options.add_argument("--disable-notifications")
        self.driver = uc.Chrome(options=self.options, seleniumwire_options=self.selenium_options)
        
    def load_page(self, url):
        self.driver.get(url)

    def close_browser(self):
        self.driver.quit()