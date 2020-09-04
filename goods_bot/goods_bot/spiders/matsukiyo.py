# -*- coding: utf-8 -*-

from goods_bot.spiders.SeleniumSpider import SeleniumSpider
from scrapy import Request
from urllib.parse import urlencode
from pprint import pprint
import struct
from goods_bot.middlewares.Selenium import SeleniumRequest
import time
import re
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from utils.oauth_request import OauthRequest
from utils.helpers import Html
from utils.helpers import Helper, File
import random
from selenium.webdriver.support.ui import WebDriverWait

class Matsukiyo(SeleniumSpider):
    '''
    用法：
    1. 爬取商品列表文件
    scrapy crawl matsukiyo -a category_file=category.txt
    2. 爬取商品
    scrapy crawl matsukiyo -a item_list_file=item_list.txt

    '''

    BASE_URL = "https://www.matsukiyo.co.jp"

    name = "matsukiyo"

    category_links = []
    category_index = 0

    options = {
        'item_header':["url", "name", "image","breadcrumb", "price", "cpde"]
    }

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'goods_bot.middlewares.Selenium.SeleniumDownloaderMiddleware': 543,
        },
        'ROBOTSTXT_OBEY' : False,
        'ITEM_PIPELINES' : {
            # 'goods_bot.pipelines.goods_json.JsonPipeline': 1000,
            'goods_bot.pipelines.csv.CsvPipeline': 2000
        },
        'SELENIUM_DRIVER_ARGUMENTS' : []
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.options = dict(self.options, **kwargs)
        self.category_file = self.options['category_file'] if 'category_file' in self.options.keys() else ''
        self.item_list_file = self.options['item_list_file'] if 'item_list_file' in self.options.keys() else ''
        self.options['item_filename'] = self.name + '_' + self.item_list_file

    def start_requests(self):
        if self.category_file:
            with open(self.category_file, 'rt') as f:
                self.category_links = [line.rstrip() for line in f]
                f.close()

            url = self.category_links[self.category_index]

            yield SeleniumRequest(url, callback= self.parse_search_item_list, 
                meta = {'wait_time': 10,'wait_until': EC.presence_of_element_located((By.CSS_SELECTOR, ".l-footer"))})

        elif self.item_list_file:
            self.item_links = []
            self.item_index = 0
            with open(self.item_list_file, 'rt') as f:
                for line in f:
                    ar = line.rstrip().split('\t')
                    self.item_links.append({
                        'item_url': self.BASE_URL + ar[0],
                        'image_url': self.BASE_URL + ar[1]
                    })
                f.close()
            self.logger.info("item_links: {}".format(len(self.item_links)))
            if self.item_links:
                yield SeleniumRequest(self.item_links[self.item_index]['item_url'], callback= self.parse_item_page,
                    meta = {'wait_time': 10,'wait_until': EC.presence_of_element_located((By.CSS_SELECTOR, ".l-footer"))})

    def parse_search_item_list(self, response):
        """
        解析检索商品列表
        """
        self.logger.info("parse_search_item_list :%s", response.url)
        output_item_filename = 'data/{}_item_list.txt'.format(self.category_file)

        File.append_line("#{}".format(response.url), output_item_filename)

        browser = response.meta['driver']
        self.click_more_until_invisable(browser, "#searchMore")
        
        # 由于点击更多加载了新的商品，所以必须更新response
        response = self.parse(response)

        item_quantity = response.css("p.left::text").extract_first()
        self.logger.info("item quantity: {}".format(item_quantity))

        if item_quantity:
            item_quantity = Helper.re_group(item_quantity, '([0-9,]+)商品', 1)
            item_quantity = int(item_quantity.replace(',', ''))
            File.append_line("# quantity:{}".format(item_quantity), output_item_filename)

        item_urls = response.css("#itemList .ttl a::attr('href')").extract()
        item_images = response.css("#itemList .img img::attr('src')").extract()
        item_index = 0

        self.logger.info("len(item_urls): {}".format(len(item_urls)))

        if len(item_urls):
            File.append_line("# links:{}".format(len(item_urls)), output_item_filename)
            while item_index < len(item_urls):
                File.append_line('{}\t{}'.format(item_urls[item_index], item_images[item_index]) , output_item_filename)
                item_index += 1

        self.category_index += 1
        if self.category_index < len(self.category_links):
            yield SeleniumRequest(self.category_links[self.category_index], callback=self.parse_search_item_list, 
                meta = {'wait_time': 10,'wait_until': EC.presence_of_element_located((By.CSS_SELECTOR, ".l-footer"))})


    def click_more_until_invisable(self, browser, btn_css):
        try:
            more_btn = browser.find_element_by_css_selector(btn_css)
            if more_btn:
                while True:
                    WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, btn_css)))
                    more_btn.click()
                    time.sleep(1 + random.uniform(3, 4))
                    self.logger.info("more_btn.is_displayed():%r", more_btn.is_displayed())
                    if not more_btn.is_displayed():
                        break
        except NoSuchElementException:
            pass

    def parse_item_page(self, response):
        """
        解析商品页面
        """
        self.logger.info("item url: %s", response.url)
        # browser = response.meta['driver']

        goods = {}
        goods['url'] = self.item_links[self.item_index]['item_url']
        goods['image'] = self.item_links[self.item_index]['image_url']

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

        # 爬取下一个商品页面
        self.item_index = self.item_index + 1
        if self.item_index < len(self.item_links):
            yield SeleniumRequest(self.item_links[self.item_index]['item_url'], callback= self.parse_item_page, 
                meta = {'wait_time': 10,'wait_until': EC.presence_of_element_located((By.CSS_SELECTOR, ".l-footer"))})
