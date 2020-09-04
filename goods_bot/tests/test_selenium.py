"""This module contains the base test cases for the ``scrapy_selenium`` package"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from shutil import which
from goods_bot.spiders.SeleniumSpider import SeleniumSpider 
import unittest

import scrapy


class BaseScrapySeleniumTestCase(unittest.TestCase):
    """Base test case for the ``scrapy-selenium`` package"""

    class SimpleSpider(SeleniumSpider):
        name = 'simple_spider'
        allowed_domains = ['python.org']
        start_urls = ['http://python.org']
        custom_settings = {
            'ITEM_PIPELINES' : {
                'goods_bot.pipelines.csv.ArticleCsvPipeline': 300
            }
        }
        def parse(self, response):
            print(self.custom_settings)
            item = {}
            item['url'] = 'test_url'
            yield item

    @classmethod
    def setUpClass(cls):
        """Create a scrapy process and a spider class to use in the tests"""

        cls.settings = {
            'SELENIUM_DRIVER_NAME': 'chrome',
            # 'SELENIUM_DRIVER_EXECUTABLE_PATH': '/usr/local/bin/chromedriver',
            'SELENIUM_DRIVER_EXECUTABLE_PATH' : 'G:/twh/prjs/bot.haibaobei-ec/chromedriver_win32/chromedriver.exe',
            'SELENIUM_DRIVER_ARGUMENTS': ['-headless']
        }
        cls.spider_klass = cls.SimpleSpider

if __name__ == '__main__':
    unittest.main()