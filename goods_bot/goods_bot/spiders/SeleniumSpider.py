# -*- coding: utf-8 -*-
"""
Selenium的爬虫基类
"""
from scrapy.spiders import Spider
from lxml import html
from six.moves.urllib.parse import urljoin
from utils.helpers import Html
from pprint import pprint

class SeleniumSpider(Spider):
    """
    Selenium的爬虫基类
    """
    def __init__(self, **kwargs):
        """
        构造函数
        """
        self.custom_settings.update(
            {
                'SPIDER_MIDDLEWARES': {
                    'goods_bot.middlewares.Selenium.SeleniumMiddleware': 543,
                }
            }
        )
        super().__init__()


    def parse(self, response):
        """
        需要重载parse函数
        """
        driver = response.meta['driver']
        return response.replace(body=str.encode(driver.page_source))

    def format_content(self, base_url, art_content):
        """
        格式化文章内容

        参数:
        * base_url 根URL
        * art_content 文章内容

        该函数对爬取到的文章的内容做以下操作:
        * 内容的<img>的src链接根据base_url替换为为绝对链接
        * 替换iframe为图片链接
        * 清除多余的标签

        """
        # 通过lxml处理content
        content = html.fromstring(art_content)

        # 替换图片
        imgs = content.cssselect("img[src]")
        for img in imgs:
            link = urljoin(base_url, img.attrib['src'])
            img.attrib['src'] = link

        # 替换链接
        alinks = content.cssselect('a[href]')
        for alink in alinks:
            link = urljoin(base_url, alink.attrib['href'])
            alink.attrib['href'] = link

        # 将iframe替换为img, 利用splash的图片API
        iframes = content.cssselect("iframe[src]")
        # 生成类似 "http://localhost:8050/render.jpeg?url=http://domain.com/"这样的uri
        splash_url = self.settings.get("SPLASH_URL")
        black_url_list = self.settings.get("BLACK_URL_LIST")
        video_url_list = self.settings.get("VIDEO_URL_LIST")
        for iframe in iframes:
            src_url = iframe.attrib['src']
            if src_url:
                link = urljoin(base_url, src_url)
                if Html.is_valid_url(link):
                    # 如果链接是黑名单链接, 删除
                    for black_url in black_url_list:
                        if link.startswith(black_url):
                            # 删除该节点
                            iframe.getparent().remove(iframe)
                            continue

                    # 如果链接是视频网站链接, 则替换为video标签
                    for video_url in video_url_list:
                        if link.startswith(video_url):
                            # 变为视频标签
                            iframe.tag = "video"
                            iframe.attrib['src'] = link
                            break

                    if iframe.tag == 'iframe':
                        # 将iframe标签替换为img标签
                        iframe.tag = "img"
                        # 将src替换为splash的render.jpeg接口
                        # wait = 2
                        # resource_timeout=20
                        # viewport=full
                        image_url = "{}/render.jpeg?wait=2&resource_timeout=20&viewport=full&url={}".format(
                            splash_url, link)
                        iframe.attrib['src'] = image_url
                else:
                    # 删除该节点
                    iframe.getparent().remove(iframe)
            else:
                # 如果src为空,删除该节点
                iframe.getparent().remove(iframe)

        # 内容处理完毕,生成HTML,并替换原有的内容
        new_content = html.tostring(content, encoding="unicode")

        return Html.clean_content(new_content)
