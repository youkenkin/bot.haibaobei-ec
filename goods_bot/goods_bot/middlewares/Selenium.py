"""This module contains the ``SeleniumMiddleware`` scrapy middleware"""

from importlib import import_module

from scrapy import signals, Request
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display
import struct

class SeleniumRequest(Request):
    """Scrapy ``Request`` subclass providing additional arguments"""

    def __init__(self, *args, **kwargs):
        """Initialize a new selenium request
        Parameters
        ----------
        wait_time: int
            The number of seconds to wait.
        wait_until: method
            One of the "selenium.webdriver.support.expected_conditions". The response
            will be returned until the given condition is fulfilled.
        screenshot: bool
            If True, a screenshot of the page will be taken and the data of the screenshot
            will be returned in the response "meta" attribute.

        Example:
        SeleniumRequest(self.START_PAGE, callback=self.parse_start_page,
            meta = {'wait_time': 10,'wait_until': selenium.webdriver.support.expected_conditions.alert_is_presen,'screenshot': False}
        )
        """
        super().__init__(*args, **kwargs)

class SeleniumDownloaderMiddleware(object):
    """Scrapy middleware handling the requests using selenium"""

    def __init__(self, driver_name, driver_executable_path, driver_arguments):
        """Initialize the selenium webdriver
        Parameters
        ----------
        driver_name: str
            The selenium ``WebDriver`` to use
        driver_executable_path: str
            The path of the executable binary of the driver
        driver_arguments: list
            A list of arguments to initialize the driver
        """
        webdriver_base_path = 'selenium.webdriver.{}'.format(driver_name)

        driver_klass_module = import_module('{}.webdriver'.format(webdriver_base_path))
        driver_klass = getattr(driver_klass_module, 'WebDriver')

        driver_options_module = import_module('{}.options'.format(webdriver_base_path))
        driver_options_klass = getattr(driver_options_module, 'Options')

        driver_options = driver_options_klass()
        for argument in driver_arguments:
            driver_options.add_argument(argument)

        driver_kwargs = {
            'executable_path': driver_executable_path,
            'options': driver_options
        }

        self.driver = driver_klass(**driver_kwargs)

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware with the crawler settings"""

        driver_name = crawler.settings.get('SELENIUM_DRIVER_NAME')
        driver_executable_path = crawler.settings.get('SELENIUM_DRIVER_EXECUTABLE_PATH')
        driver_arguments = crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS')

        if not driver_name or not driver_executable_path:
            raise NotConfigured(
                'SELENIUM_DRIVER_NAME and SELENIUM_DRIVER_EXECUTABLE_PATH must be set'
            )

        middleware = cls(
            driver_name=driver_name,
            driver_executable_path=driver_executable_path,
            driver_arguments=driver_arguments
        )

        crawler.signals.connect(middleware.spider_closed,signal=signals.spider_closed)
        signals.engine_started

        return middleware

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        meta_keys = request.meta.keys()

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if  'wait_until' in meta_keys and 'wait_time' in meta_keys:
            WebDriverWait(self.driver, request.meta['wait_time']).until(
                request.meta['wait_until']
            )

        if 'screenshot' in meta_keys:
            request.meta['screenshot'] = self.driver.get_screenshot_as_png()

        body = str.encode(self.driver.page_source)

        # Expose the driver via the "meta" attribute
        request.meta['driver'] = self.driver

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )

    def spider_closed(self):
        """Shutdown the driver when spider is closed"""
        self.driver.quit()