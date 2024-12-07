from amazon_scraper_class import AmazonPWrightScraper

class ScraperFactory:
    def get_scraper(self, platform, homepage=None, proxy=None, hasSignIn=False, productNames=["Gaming Chair", "Gaming Headset"],account={"username": "diepbaothien10x@gmail.com", "password": "thien1"}, headless=False):
        if platform == "amazon":
            return AmazonPWrightScraper(homepage="https://amazon.com" if homepage == None else homepage
                                        , hasSignIn=hasSignIn
                                        , productNames=productNames
                                        , account=account
                                        , headless=headless
                                        , proxy=proxy)
        # elif platform == "ebay":
        #     return EbayScraper()
        else:
            raise ValueError(f"No scraper available for {platform}")