# -*- coding: utf-8 -*-
"""
"""
import datetime
from peewee import Model
from peewee import FixedCharField,CharField, DateTimeField, BooleanField, IntegerField, TextField
from goods_bot.database import DATABASE_PROXY

class BaseModel(Model):
    """
    数据库Model基类
    """

    def set_data(self, item):
        """
        Set data by dict
        """
        for k in item:
            if k in self.props():
                setattr(self, k, item[k])

    def get_data(self):
        """
        Get a copy of data
        """
        return self._data.copy()

    @classmethod
    def props(cls):
        """
        Get all model properties
        """
        return [i for i in cls.__dict__.keys() if i[:1] != '_']

    class Meta:
        """
        Meta
        """
        database = DATABASE_PROXY  # Use proxy for our DB.


class ArticleList(BaseModel):
    """
    文章列表
    """
    md5 = FixedCharField(index=True, default="", max_length=32, help_text=u"文章标题+来源的md5值")
    origin = CharField(index=True, default="", help_text=u"来源")
    url = CharField(index=True, default="", help_text=u"文章链接")
    cover = CharField(help_text=u"封面图片链接", null=True)
    title = CharField(help_text=u"标题", null=True)
    author = CharField(null=True, default="", max_length=100, help_text=u"作者")
    post_date = DateTimeField(index=True, null=True, help_text=u"文章提交日期")
    create_date = DateTimeField(default=datetime.datetime.now)
    is_crawled = BooleanField(default=False, help_text="爬过标志")


class Article(BaseModel):
    """
    文章
    """
    md5 = FixedCharField(index=True, default="", max_length=32, help_text=u"文章标题+来源的md5值")
    news_source_id = IntegerField(null=True, index=True, help_text=u"信息源id,来自于encore的target.id")
    is_forward = BooleanField(default=False, help_text=u"是否转发")
    origin = CharField(index=True, default="", help_text=u"来源")
    url = CharField(index=True, default="", help_text=u"文章链接")
    cover = CharField(help_text=u"封面图片链接", null=True)
    title = CharField(help_text=u"标题", null=True)
    author = CharField(null=True, index=True, default="", max_length=100, help_text=u"作者")
    author_photo = CharField(null=True, default="", help_text="作者头像图片链接")
    post_date = DateTimeField(null=True, help_text=u"文章提交日期")
    images = TextField(null=True, help_text=u"不在文章内容的图片链接")
    create_date = DateTimeField(null=True, help_text=u"最后更新日期", default=datetime.datetime.now)
    is_crawled = BooleanField(default=False, help_text="爬过标志")
    is_asyn = BooleanField(default=False, help_text="同步成功标志")
    content = TextField(help_text=u"文章内容(包含图片和视频链接)")
    videos = TextField(null=True, help_text=u"不在文章内容的视频链接")
    old_content = TextField(help_text=u"文章原始内容")
    response = TextField(null=True, help_text=u"服务器返回的Response内容")
    memo = TextField(null=True, help_text=u"备注")