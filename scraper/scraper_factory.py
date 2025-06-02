from .amazon_scraper_class import AmazonPWrightScraper
from .finance_scraper_class import FinanceScraperClass

class ScraperFactory:
    def get_scraper(self, platform, homepage=None, proxy=None, hasSignIn=False, productNames=["Gaming Chair", "Gaming Headset"],account={"username": "diepbaothien10x@gmail.com", "password": "thien1"}, headless=False, maxQueueSize = 0, queuesNum = 2, timeRange = '01-01-2021 - 31-12-2024'):
        if platform == "amazon":
            print("Retrieve Amazon Configuration")
            # return AmazonPWrightScraper(homepage="https://amazon.com" if homepage == None else homepage
            #                             , hasSignIn=hasSignIn
            #                             , productNames=productNames
            #                             , account=account
            #                             , headless=headless
            #                             , proxy=proxy
            #                             , maxQueueSize=maxQueueSize
            #                             , queuesNum=queuesNum)
        # elif platform == "ebay":
        #     return EbayScraper()
        elif platform == "finance":
            print("Retrieve Finance Scraper Configuration")
            return FinanceScraperClass(homepage="https://cafef.vn/du-lieu/lich-su-giao-dich-symbol-vnindex/trang-1-0-tab-1.chn" if homepage == None else homepage
                                        , hasSignIn=hasSignIn
                                        , productNames=productNames
                                        , account=account
                                        , headless=headless
                                        , proxy=proxy
                                        , maxQueueSize=maxQueueSize
                                        , queuesNum=queuesNum
                                        , timeRange= timeRange)
        else:
            raise ValueError(f"No scraper available for {platform}")
        