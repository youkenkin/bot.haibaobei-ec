# -*- coding: utf-8 -*-
import hashlib
import os
import json
from utils.helpers import File, JSON


class JsonPipeline(object):
    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        filename = "data/" + spider.name
        if 'goods_no' in item.keys() and item['goods_no']:
            filename = filename + "/" + item['goods_no'] + ".json"
        else:
            filename = filename + "/" + hashlib.md5(JSON.dumps(item).encode('utf-8')).hexdigest() + '.json'

        File.check_and_make_dir(os.path.dirname(filename))

        with open(filename, 'wt') as f:
            JSON.dump(item, f)
            f.close()

        return item
