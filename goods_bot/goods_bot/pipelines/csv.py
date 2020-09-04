# -*- coding: utf-8 -*-
import csv

class CsvPipeline(object):

    def open_spider(self, spider):
        filename = "data/" + spider.options['item_filename'] + '.csv'

        self.csvfile = open(filename, 'wt' , encoding='utf-8', newline='')
        self.csvwriter = csv.writer(self.csvfile, 'excel-tab')
        self.csvheader = spider.options['item_header']
        self.csvwriter.writerow(self.csvheader)

    def close_spider(self, spider):
        self.csvfile.close()
    
    def process_item(self, item, spider):
        self.csvwriter.writerow(CsvPipeline.dict2list(item, self.csvheader))
        self.csvfile.flush()
        return item

    @staticmethod
    def dict2list(dict_src, key_list):
        ls = []
        for key in key_list:
            ls.append(dict_src[key])
        return ls

