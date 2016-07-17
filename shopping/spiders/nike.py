# -*- coding: utf-8 -*-
import scrapy
import json
from shopping.items import ShoppingItem
import sys
import datetime


class NikeSpider(scrapy.Spider):
    name = "nike"
    allowed_domains = ["nike.com"]

    init_link = 'http://store.nike.com/html-services/gridwallData?country=US&lang_locale=en_US&gridwallPath=new-mens/meZ7pu&pn=1'
    start_urls = (
        init_link,
    )

    def main_process(self, response):
        item = ShoppingItem()
        x_path = [
            '//script[@id="product-data"]/text()',
        ]
        for v in x_path:
            r_data = response.xpath(v).extract()
            if r_data:
                break

        if r_data == '':
            print('FUCKINGG=============================')
            sys.exit(-1)
        try:
            data = json.loads(r_data[0].strip())
            item['pid'] = data.get('productId')
            item['pgid'] = data.get('productGroupId')
            item['pname'] = data.get('displayName')
            item['pdesc'] = data.get('content')
            item['pimage'] = data.get('thumbnailUrl')
            item['psize'] = data.get('trackingData').get('sizeRun')
            item['psku'] = data.get('skuContainer').get(
                'productSkus')[0].get('sku')
            item['pdate'] = datetime.datetime.utcfromtimestamp(
                data.get('startDate') / 1000).strftime('%Y-%m-%d %H:%M:%S')
            item['pcolor'] = data.get('colorDescription')
            item['pprice'] = data.get('localPrice')[1:]
            item['pclass'] = '1'
            yield item
        except:
        	pass

    def parse(self, response):
        data = json.loads(response.body.decode('utf-8'))
        if data.get('sections') and data.get('sections')[0].get('products'):
            for v in data.get('sections')[0].get('products'):
                yield scrapy.Request(v.get('pdpUrl'), callback=self.main_process)

        next_link = data.get('nextPageDataService')
        if next_link:
            if int(next_link[-1]) < 3:
                yield scrapy.Request(next_link, callback=self.parse)
