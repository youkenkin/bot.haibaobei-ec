# -*- coding: utf-8 -*-
import sys
import os
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
from utils.helpers import File, Helper
import re

import pandas
from openpyxl import load_workbook

def extract_jan(cpde):
    return Helper.re_group(cpde,r'JANコード ：(\d+)', 1)

def extract_maker(cpde):
    return Helper.re_group(cpde,r'メーカー ：(.*?)[\xa0|\|]', 1)

def extract_brand(cpde):
    return Helper.re_group(cpde,r'ブランド ：(.*?)JANコード ：', 1)

def extract_mno(cpde):
    return Helper.re_group(cpde,r'医療機器承認番号 ：([a-zA-Z0-9]*)', 1)
    
df = pd.read_excel('matsukiyo_data.xlsm', sheet_name='DATA')

print(df)

# book = load_workbook('matsukiyo_data.xlsm')
# writer = pd.ExcelWriter('matsukiyo_data.xlsm', engine='openpyxl') 
# writer.book = book

## ExcelWriter for some reason uses writer.sheets to access the sheet.
## If you leave it empty it will not know that sheet Main is already there
## and will create a new sheet.
# writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

# df.to_excel(writer, "Main", cols=['Diff1', 'Diff2'])

# writer.save()

def parse_cpde(cpde):
    r = {}
    r['jan'] = extract_jan(cpde)
    r['maker'] = extract_maker(cpde), 
    r['brand'] = extract_brand(cpde),
    r['mno'] = extract_mno(cpde)
    return r

def parse_breadcrumb(breadcrumb):
    return Helper.re_groups(breadcrumb, r'トップ >(.*?)>(.*)')

for index, row in df.iterrows():
    cpde = row['cpde']

    print(cpde)
    r = parse_cpde(cpde)

    price = row['price']
    price = Helper.multireplace(price, {",":"", "円":""})
    print(price)

    breadcrumb = row['breadcrumb']
    top_category, sub_category = parse_breadcrumb(breadcrumb)

    print(top_category, sub_category)

    image_path = File.download(row['image'], 'data/images/{}.jpeg'.format(r['jan']))
    print(image_path)
   
    if index > 10:
        break

