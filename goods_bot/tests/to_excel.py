# -*- coding: utf-8 -*-
import sys
import os
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
from utils.helpers import File, Helper
import re
import sys
from tqdm import tqdm

input_file = sys.argv[1]
output_file = sys.argv[2]

def extract_jan(cpde):
    return Helper.re_group(cpde,r'JANコード ：(\d+)', 1)

def extract_maker(cpde):
    return Helper.re_group(cpde,r'メーカー ：(.*?)[\xa0|\|]', 1)

def extract_brand(cpde):
    return Helper.re_group(cpde,r'ブランド ：(.*?)JANコード ：', 1)

def extract_mno(cpde):
    return Helper.re_group(cpde,r'医療機器承認番号 ：([a-zA-Z0-9]*)', 1)

xls = pd.ExcelFile(input_file)
df1 = pd.read_excel(xls, 'DATA')
df2 = pd.read_excel(xls, 'REPORT')

# print(df1)
# print(df2)

def parse_cpde(cpde):
    r = {}
    r['jan'] = extract_jan(cpde)
    r['maker'] = extract_maker(cpde)
    r['brand'] = extract_brand(cpde)
    r['mno'] = extract_mno(cpde)
    return r

def parse_breadcrumb(breadcrumb):
    return Helper.re_groups(breadcrumb, r'トップ >(.*?)>(.*)')


for index, row in tqdm(df1.iterrows()):
    if pd.notnull(row['name']):
        cpde = row['cpde']
        r = parse_cpde(cpde)

        price = row['price']
        price = Helper.multireplace(price, {",":"", "円":""})

        breadcrumb = row['breadcrumb']
        top_category, sub_category = parse_breadcrumb(breadcrumb)

        # image_path = File.download(row['image'], 'data/images/{}.jpeg'.format(r['jan']))
        df2.loc[index] = [index, top_category, sub_category, row['image'], r['jan'], row['name'], price, r['maker'], r['brand'], row['url']]

        # image_path = File.download(row['image'], 'data/images/{}.jpeg'.format(r['jan']))
        # df2.loc[index] = [index, top_category, sub_category, image_path, r['jan'], row['name'], price, r['maker'], r['brand'], row['url']]

df2.to_excel(output_file, index=None)
