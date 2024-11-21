from abc import ABC, abstractmethod
from scraper_base_class import BaseScraper

class WebsiteScraper(ABC, BaseScraper):
    @abstractmethod
    def sign_in(self, username, password):
        pass

    @abstractmethod
    def search_product(self, product_name):
        pass

    @abstractmethod
    def get_all_products_links(self):
        pass
    
    @abstractmethod
    def get_product_detail(self, href):
        pass

    @abstractmethod
    def parse_data(self):
        pass

    
