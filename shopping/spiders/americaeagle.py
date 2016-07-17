# -*- coding: utf-8 -*-
import scrapy
import json
from shopping.items import ShoppingItem
import sys
import datetime
import logging

class AmericanEagleSpider(scrapy.Spider):
    name = "ae"
    allowed_domains = ["ae.com"]

    init_link = 'http://www.forever21.com/Product/Category.aspx?br=plus&category=plus-size-new-arrivals-tops'
    start_urls = (
        init_link,
    )

    def main_process(self, response):
        item = ShoppingItem()
        x_path = {
            'size': '//*[@role="menuitem" and @data-size]/@data-size',
            'description': '//meta[@property="og:description"]/@content',
            'productprice': '//*[@id="psp-regular-price"]/@content',
            'productname': '//meta[@property="og:title"]/@content',

        }
        re_gex = {
            'color': 'colorName:"([^"]+)"',
            'productid': 'br_data.prod_id = "([^"]+)"',
            'productcat': 'br_data.cat = "([^"]+)"',
            'productsku': 'br_data.sku = \'([^\']+)\'',
            
            'productimage' : 'socioPhoto\': \'([^\']+)\''
        }
        rep = scrapy.selector.Selector(response)
        item['pid'] = int(''.join(rep.re(re_gex.get('productid'))))
        # item['pgid'] = ''.join(rep.re(re_gex.get('productcat')))
        item['pgid'] = 0
        item['pname'] = ''.join(rep.re(re_gex.get('productname')))
        item['pdesc'] = ''.join(rep.xpath(x_path.get('description')).extract())
        item['pimage'] = ''.join(rep.re(re_gex.get('productimage')))
        item['psize'] = '|'.join(rep.xpath(x_path.get('size')).extract()).strip()
        item['psku'] = ''.join(rep.re(re_gex.get('productsku')))
        item['pdate'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['pcolor'] = '|'.join(rep.xpath(x_path.get('color')).extract())
        item['pprice'] = float(''.join(rep.re(re_gex.get('productprice'))))
        item['pclass'] = 0
        yield item

    def _get_product_link(self,rep):
        data = rep.xpath('//*[contains(@class,"category-product") and @itemscope @itemtype]').extract()
        if not data:
            raise "[SHIT] Something wrong"
            return []
        return data

    def parse(self, response):
        # net to get all product links one time
        links = self._get_product_link(response)
        for link in links:
            yield scrapy.Request('https://www.ae.com'+str(link), callback=self.main_process)
        
