from goods_bot.spiders.SeleniumSpider import SeleniumSpider
from scrapy import Request
from urllib.parse import urlencode

class ChordieSpider(SeleniumSpider):
    name = "chordie"

    BASE_URL = "https://www.chordie.com/"
    custom_settings = {
        'ITEM_PIPELINES' : {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'goods_bot.pipelines.json.JsonPipeline': 1000
        },
        'FILES_STORE' : 'data',
    }

    def start_requests(self):
        url = "https://www.chordie.com/chords.php"
        yield Request(url, callback=self.parse_chords_url)

    def parse_chords_url(self, response):
        """
        解析和弦一览URL
        """
        self.logger.info("parse_chords_url :%s", response.url)
        for chord_link in response.css('a[href^="voicings.php?tuning=EADGBE&"]'):
            chord_url = self.BASE_URL + chord_link.css("::attr(href)").extract_first()
            self.logger.info('chord_link: %s', chord_link.css("::attr(href)").extract_first())
            yield Request(chord_url, callback=self.parse_chord)

    def parse_chord(self, response):
        """
        解析和弦图片和名称
        """
        self.logger.info("parse_chords: %s", response.url)
        for chord_img in response.css("div.topContent>img[src^='https://www.chordie.com//ramimages/']"):
            item = {}
            item['chord_name'] = chord_img.css("::attr(title)").extract_first()
            item['chord_img'] = chord_img.css("::attr(src)").extract_first()
            item['file_urls'] = chord_img.css("::attr(src)").extract()
            self.logger.info("%s: %s", item['chord_name'], item['chord_img'])
            yield item
