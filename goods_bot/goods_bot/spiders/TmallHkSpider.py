#https://detail.tmall.hk
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

from utils.oauth_request import OauthRequest
from utils.helpers import Html
import random
from selenium.webdriver.support.ui import WebDriverWait

class TmallHk(SeleniumSpider):
    JP_CN = 16.27

    name = "TmallHk"

    #START_PAGE = "https://mikihouse.tmall.hk/search.htm?viewType=list&pageNo=%d"
    START_PAGE = "file:///home/telesoho/Downloads/mikihouse/MIKIHOUSE海外旗舰店官网 - 天猫国际_%d.html"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'goods_bot.middlewares.Selenium.SeleniumDownloaderMiddleware': 543,
        },
        'ROBOTSTXT_OBEY' : False,
        'ITEM_PIPELINES' : {
            'goods_bot.pipelines.goods_json.JsonPipeline': 1000
        },
        'SELENIUM_DRIVER_ARGUMENTS' : ["--user-data-dir=/home/telesoho/prjs/bot.haibaobei-ec/goods_bot/profile" ]
    }

    def __init__(self, name=None, **kwargs):
        self.log("__init__")
        # self.custom_settings.update({
        #     'ITEM_PIPELINES' : {
        #         'goods_bot.pipelines.json.JsonPipeline': 1000
        #     }
        # })

    def start_requests(self):
        self.page = 1
        self.total_page = 12
        url = self.START_PAGE % self.page
        # yield Request(url, callback=self.parse_start_page)

        # yield SeleniumRequest(self.START_PAGE % self.page, callback=self.parse_start_page, 
        #     meta = {'wait_time': 10,'wait_until': EC.presence_of_element_located((By.ID, "page-footer"))})
        # url = "https://detail.tmall.hk/hk/item.htm?spm=a1z10.3-b-s.w4011-14575382531.101.256d4bc686Ds1X&id=548477908545&rn=843661e67ed5a7da79f67abab14d1cb5&abbucket=17"
        yield SeleniumRequest(url, callback= self.parse_start_page, 
            meta = {'wait_time': 10,'wait_until': EC.presence_of_element_located((By.ID, "page-footer"))})

    def parse_start_page(self, response):
        """
        解析首页
        """
        self.logger.info("parse_start_page :%s", response.url)
        self.item_urls = response.css(".item-wrap .item .detail-info .title a::attr('href')").extract()
        if len(self.item_urls):
            self.item_index = 0 
            yield SeleniumRequest(self.item_urls[self.item_index], callback= self.parse_item_page
            # , meta = {'wait_time': 10,'wait_until': EC.presence_of_element_located((By.ID, "page-footer"))}
                )

    def scroll_down(self, browser):
        """A method for scrolling the page."""

        # Get scroll height.
        last_height = browser.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to the bottom.
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load the page.
            time.sleep(6)
            # Calculate new scroll height and compare with last scroll height.
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        browser.execute_script("window.scrollTo(0, 0)")

    def parse_item_page(self, response):
        """
        解析商品页面
        """
        self.logger.info("item url: %s", response.url)
        browser = response.meta['driver']

        close_btn = browser.find_element_by_css_selector("#sufei-dialog-close")
        if close_btn:
            WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, "sufei-dialog-close")))
            close_btn = browser.find_element_by_css_selector("#sufei-dialog-close")
            close_btn.click()
        time.sleep(1 + random.uniform(2, 5))

        self.scroll_down(browser)

        time.sleep(1 + random.uniform(2, 5))

        sell_price = response.css('#J_StrPriceModBox .tm-price::text').extract_first()

        goods = {}

        # 查找SKU名称
        sku_pvs_names = {}
        tb_skus = response.css(".tb-key .tb-sku dl.tb-prop ul[data-property]")
        for tb_sku in tb_skus:
            sku_name = tb_sku.css("::attr('data-property')").extract_first()
            sku_values = tb_sku.css("li[data-value]")
            for sku_value in sku_values:
                value = sku_value.css("::attr('data-value')").extract_first()
                sku_pvs_names[value] = sku_name

        # 分析javascript的JSON,获取SKU数据
        regex = r"TShop\.Setup\([^{]*({.*})"
        matches = re.search(regex, response.body.decode("utf-8"), re.MULTILINE)

        sku_infos = []
        if matches:
            item_json = {}
            item_json = matches.group(1)
            item_json = json.loads(item_json)
            if 'valItemInfo' in item_json.keys():
                skuList = item_json['valItemInfo']['skuList']
                skuMap = item_json['valItemInfo']['skuMap']
                for sku in skuList:
                    sku_info = {}
                    names = sku['names'].split(' ')
                    pvs = sku['pvs'].split(';')
                    spec_array = {}
                    for i, pv in enumerate(pvs):
                        pvs_name = sku_pvs_names[pv]
                        # names[i] = "%s:%s" % (pvs_name, names[i])
                        spec_array[pvs_name] = names[i]
                    # sku_info['name'] = ';'.join(names)
                    sku_info['spec_array'] = spec_array
                    sku_info['products_no'] = sku['skuId']
                    # sku_info['pvs'] = sku['pvs']
                    sku_map = skuMap[";%s;" % sku['pvs']]
                    sku_info['sell_price'] = float(sku_map['price'])
                    sku_info['jp_price'] = float(sku_map['price']) * self.JP_CN
                    sku_info['store_nums'] = int(sku_map['stock'])
                    sku_infos.append(sku_info)
        goods['product_spec'] = sku_infos

        J_AttrULs = response.css("#J_AttrList #J_AttrUL li::text").extract()
        for attr in J_AttrULs:
            if attr.startswith("货号:"):
                goods['goods_no'] = attr.replace("货号:\xa0", "")
            elif attr.startswith("品牌:"):
                goods['brand_name'] = attr.replace("品牌:\xa0", "")

        # 处理商品展示轮播图片
        # browser.execute_script()
        images = []
        thumb_imgs = response.css("#J_UlThumb a img::attr('src')").extract()
        for thumb_img in thumb_imgs:
            element_thumb = browser.find_element_by_css_selector("#J_UlThumb a img[src='%s']" % thumb_img)
            element_thumb.click()
            time.sleep(1 + random.uniform(5, 10))
            element_img = browser.find_element_by_css_selector("img#J_ImgBooth")
            if element_img:
                images.append(element_img.get_attribute("src"))
        goods['images'] = images

        # 处理商品详情
        content = browser.find_element_by_css_selector(".content")
        if content:
            goods['content'] = Html.clean_content(content.get_attribute('innerHTML'))

        # 商品名称
        goods_name = browser.find_element_by_css_selector('#J_DetailMeta .tb-detail-hd h1')
        if goods_name:
            goods_name = goods_name.get_attribute('innerText')
            # goods['name'] = response.css('#J_DetailMeta .tb-detail-hd h1::text').extract_first().strip()
            goods['name'] = goods_name.strip()


        # 价格
        # sell_price = response.css('#J_StrPriceModBox .tm-price::text').extract_first()
        sell_price = browser.find_element_by_css_selector('#J_StrPriceModBox .tm-price')
        if sell_price:
            goods['sell_price'] = float(sell_price.get_attribute("innerText"))
            goods['jp_price'] = goods['sell_price'] * self.JP_CN

        yield goods

        # 爬取下一个商品页面
        self.item_index = self.item_index + 1
        if self.item_index < len(self.item_urls):
            yield SeleniumRequest(self.item_urls[self.item_index], callback= self.parse_item_page)
        else:
            if self.page < self.total_page:
                self.page = self.page + 1
                yield SeleniumRequest(self.START_PAGE % self.page, callback=self.parse_start_page)
