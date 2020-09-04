from goods_bot.spiders.SeleniumSpider import SeleniumSpider
from scrapy import Request
from urllib.parse import urlencode

class ShopingYahooCoJp(SeleniumSpider):
    name = "shoping.yahoo.co.jp"

    # Instagram链接
    SEARCH_PAGE = "http://shopping.yahoo.co.jp/search?p={keyword}"
    
    def get_keyword_list(self):
        keywords = ['abc', '1+23']
        return keywords

    def start_requests(self):
        keyword_list = self.get_keyword_list()
        index = 0
        for keyword in keyword_list:
            url = self.SEARCH_PAGE.format(keyword=urlencode(keyword))
            priority = 100000 - index
            index = index + 1

            yield Request(
                url, callback=self.parse_search_page,
                priority=priority,
            )

    def parse_search_page(self, response):
        """
        解析
        """
        self.logger.info("parse_search_page :%s", response.url)
        item = {}
        item['url'] = response.url
        yield item
