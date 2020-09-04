# -*- coding: utf-8 -*-
"""
初始化爬虫数据库
"""
from __future__ import print_function
from peewee import SqliteDatabase
from scrapy.commands import ScrapyCommand
from goods_bot.database import OpenSqliteDatabase
import goods_bot.database.models as model
from scrapy.utils.project import get_project_settings
import os
from utils.helpers import Time

class Command(ScrapyCommand):
    """
    初始化爬虫命令
    """
    default_settings = {'LOG_ENABLED': False,
                        'SPIDER_LOADER_WARN_ONLY': True}

    def short_desc(self):
        return "Init jcbot database"

    def run(self, args, opts):
        resetdb()


def resetdb():
    """
    初始化爬虫数据库
    """
    database_file = get_project_settings().get('DATABASE')
    if os.path.isfile(database_file):
        # 备份原数据库
        newfile = "{}.{}".format(database_file, Time.timestamp_now())
        os.rename(
            database_file,
            newfile
        )
        print("old database has beed backup to:%s" % newfile)

    database = OpenSqliteDatabase(database_file)
    database.create_tables([model.Article, model.ArticleList])
    database.close()