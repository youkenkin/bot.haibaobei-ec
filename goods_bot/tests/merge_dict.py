class Base:
    custom_settings = None

    def __init__(self, name=None, **kwargs):
        self.custom_settings.update(
            {
                'SPIDER_MIDDLEWARES': {
                    'goods_bot.middlewares.Selenium.SeleniumMiddleware': 543,
                }
            }
        )


class Sub(Base):
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'goods_bot.pipelines.json.JsonPipeline': 1000
        },
        'FILES_STORE': 'data',
    }

    def print(self):
        print(self.custom_settings)

sub = Sub()
sub.print()