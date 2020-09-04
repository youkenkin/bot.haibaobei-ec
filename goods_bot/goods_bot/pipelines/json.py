# -*- coding: utf-8 -*-
import json

class JsonPipeline(object):
    def open_spider(self, spider):
        self.jsonfile = open('data/items.json', 'wt')
        self.jsonfile.write('[')

    def close_spider(self, spider):
        self.jsonfile.write(']')
        self.jsonfile.close()
    
    def process_item(self, item, spider):
        self.jsonfile.write(json.dumps(item))
        self.jsonfile.flush()
        self.jsonfile.write(',')
        return item

    @staticmethod
    def dict2list(dict_src, key_list):
        ls = []
        for key in key_list:
            ls.append(dict_src[key])
        return ls
