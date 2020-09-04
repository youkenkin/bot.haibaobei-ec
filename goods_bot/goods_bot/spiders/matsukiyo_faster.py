# -*- coding: utf-8 -*-
from goods_bot.spiders.SeleniumSpider import SeleniumSpider
from scrapy import Request
from urllib.parse import urlencode
from utils.helpers import Html
from utils.helpers import Helper, File

class matsukiyoFasterSpider(SeleniumSpider):
    name = "matsukiyo_faster"

    BASE_URL = "https://www.matsukiyo.co.jp"

    custom_settings = {
        'ITEM_PIPELINES' : {
            # 'scrapy.pipelines.files.FilesPipeline': 1,
            # 'goods_bot.pipelines.json.JsonPipeline': 1000
            'goods_bot.pipelines.csv.CsvPipeline': 2000
        },
        'FILES_STORE' : 'data',
    }

    options = {
        'item_header':["url", "name", "image","breadcrumb", "price", "cpde"]
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.options = dict(self.options, **kwargs)
        self.item_list_file = self.options['item_list_file'] if 'item_list_file' in self.options.keys() else ''
        self.options['item_filename'] = self.name + '_' + self.item_list_file

    def start_requests(self):
        if self.item_list_file:
            item_links = []
            with open(self.item_list_file, 'rt') as f:
                for line in f:
                    ar = line.rstrip().split('\t')
                    item_links.append({
                        'item_url': self.BASE_URL + ar[0],
                        'image_url': self.BASE_URL + ar[1]
                    })
                f.close()
            self.logger.info("item_links: {}".format(len(item_links)))
            for item_link in item_links:
                url = item_link['item_url']
                yield Request(url, callback=self.parse_item_url, 
                    meta = {'item_link': item_link})

    def parse_item_url(self, response):
        """
        解析商品
        """
        self.logger.info("parse_item_url :%s", response.url)
        item_link = response.meta['item_link']
        
        goods = {}

        goods['url'] = item_link['item_url']
        goods['image'] = item_link['image_url']

        name = response.css('div.goodsBox h3::text').extract_first()
        price = response.css('.goodsDetail p.price span span:nth-of-type(1)::text').extract_first()
        breadcrumb = response.css('div.breadcrumb ul').extract_first()
        cpde = response.css('p.cpde').extract_first()

        breadcrumb = Html.clean_html(breadcrumb)
        cpde = Html.clean_html(cpde)

        print(price, breadcrumb, cpde)

        goods['name'] = name
        goods['breadcrumb'] = breadcrumb
        goods['price'] = price
        goods['cpde'] = cpde

        yield goods
