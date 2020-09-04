# -*- coding: utf-8 -*-
"""
将管道中的数据保存到sqlite数据库
"""
import logging
import traceback

from goods_bot.database import OpenSqliteDatabase
import goods_bot.database.models as model 


logger = logging.getLogger(__name__)

class ArticlePipeline(object):
    """
    文章保存到sqlite
    """

    database = None

    def open_spider(self, spider):
        """
        打开爬虫时,同时打开数据库
        """
        self.database = OpenSqliteDatabase(spider.settings.get('DATABASE'))

    def close_spider(self, spider):
        """
        关闭爬虫时,同时关闭数据库
        """
        if self.database:
            self.database.close()

    def process_item(self, item, spider):
        """
        处理每个Item
        """

        # 查找是否存在对应的文章
        try:
            art = model.Article.get(model.Article.md5 == item['md5'])
        except model.Article.DoesNotExist:
            art = model.Article(md5=item['md5'])

        # 保存文章
        try:
            art.set_data(item)
            art.save()
            logger.info("Article %s saved!", item['url'])
        except:
            logger.error("Article %s save failed!", item['url'])
            logger.error("Because:%s", traceback.format_exc())

        return item

