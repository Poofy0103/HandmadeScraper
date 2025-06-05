# from .amazon_scraper_class import AmazonPWrightScraper
from .finance_scraper_class import FinanceScraperClass
from .news_scraper_class import NewsScraperClass
from .macro_metrics_scraper_class import MacroMetricsScraperClass
from .travelling_scraper_class_copy import TravellingScraperClass

class ScraperFactory:
    def get_scraper(self, platform, homepage=None, proxy=None, hasSignIn=False, stockCodes=["Gaming Chair", "Gaming Headset"],account={"username": "diepbaothien10x@gmail.com", "password": "thien1"}, headless=False, maxQueueSize = 0, queuesNum = 2, timeRange = '01-01-2021 - 31-12-2024'):
        if platform == "finance":
            print("Retrieve Finance Scraper Configuration")
            return FinanceScraperClass(homepage="https://www.booking.com/searchresults.en-gb.html?label=en-vn-booking-desktop-WeZI9wwaGAAqHXeGoKbrHQS652828997899%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atikwd-65526620%3Alp9198864%3Ali%3Adec%3Adm&gclid=Cj0KCQjwgIXCBhDBARIsAELC9Zj8DwnfTSotcbQLWXSb_2k986ObVIOJw8qQzlzGxvp681nwUjPeAXEaAkIwEALw_wcB&aid=2311236&checkin=2025-06-07&checkout=2025-06-08&dest_id=-3730078&dest_type=city&group_adults=null&req_adults=null&no_rooms=null&group_children=null&req_children=null" if homepage == None else homepage
                                        , hasSignIn=hasSignIn
                                        , stockCodes=stockCodes
                                        , account=account
                                        , headless=headless
                                        , proxy=proxy
                                        , maxQueueSize=maxQueueSize
                                        , queuesNum=queuesNum
                                        , timeRange= timeRange)
        elif platform == "news":
            print("Retrieve Finance Scraper Configuration")
            return NewsScraperClass(homepage="https://cafef.vn/du-lieu/tin-doanh-nghiep/{}/event.chn" if homepage == None else homepage
                                        , hasSignIn=hasSignIn
                                        , stockCodes=stockCodes
                                        , account=account
                                        , headless=headless
                                        , proxy=proxy
                                        , maxQueueSize=maxQueueSize
                                        , queuesNum=queuesNum
                                        , timeRange= timeRange)
        elif platform == "macro":
            print("Retrieve Finance Scraper Configuration")
            return MacroMetricsScraperClass(homepage="https://cafef.vn/du-lieu/tin-doanh-nghiep/{}/event.chn" if homepage == None else homepage
                                        , hasSignIn=hasSignIn
                                        , account=account
                                        , headless=headless
                                        , proxy=proxy
                                        , maxQueueSize=maxQueueSize
                                        , queuesNum=queuesNum
                                        , timeRange= timeRange)
        elif platform == "travelling":
            print("Retrieve Finance Scraper Configuration")
            return TravellingScraperClass(homepage="https://www.booking.com/" if homepage == None else homepage
                                        , hasSignIn=hasSignIn
                                        , account=account
                                        , productNames=stockCodes
                                        , headless=headless
                                        , proxy=proxy
                                        , maxQueueSize=maxQueueSize
                                        , queuesNum=queuesNum)
        else:
            raise ValueError(f"No scraper available for {platform}")
        