from abc import ABC, abstractmethod
from .scraper_base_class import PyppeteerBaseScraper, PlaywrightBaseScraper

class WebsitePyppetScraper(ABC, PyppeteerBaseScraper):
    @abstractmethod
    async def sign_in(self, username, password):
        pass

    @abstractmethod
    async def search_product(self, product_name):
        pass

    @abstractmethod
    async def get_all_products_links(self):
        pass

class WebsitePWrightScraper(ABC, PlaywrightBaseScraper):
    @abstractmethod
    async def sign_in(self, username, password):
        pass

    @abstractmethod
    async def search_product(self, product_name):
        pass

    @abstractmethod
    async def get_all_products_links(self):
        pass

    
