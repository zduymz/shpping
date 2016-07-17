# -*- coding: utf-8 -*-
import scrapy
import json
from shopping.items import ShoppingItem
import sys
import datetime
import logging

class HollistercoSpider(scrapy.Spider):
    name = "hollisterco"
    allowed_domains = ["hollisterco.com"]

    init_link = 'https://www.hollisterco.com/shop/wd/guys-shirts-tops'
    start_urls = (
        init_link,
    )

    def main_process(self, response):
        item = ShoppingItem()
        x = {
            'productname': '//meta[@property="og:title"]/@content',
            'productimage': '//meta[@property="og:image"]/@content',
            'size': '//ul[@data-defining-attribute-name="Size"]/li/@data-defining-attribute-value',
            'description': '//meta[@property="og:description"]/@content',
            'productprice': '//meta[@property="og:price:standard_amount"]/@content',
            'color': '//ul[@data-defining-attribute-name="Color"]/li/@data-defining-attribute-value',
            'productid': '//input[@name="productId"]/@value',
            'productcat': '//input[@name="catId"]/@value',
            'productsku': '//input[@name="longSku"]/@value',
        }
        
        item['pid'] = int(''.join(response.xpath(x['productid']).extract()))
        item['pgid'] = int(''.join(response.xpath(x['productcat']).extract()))
        item['pname'] = ''.join(response.xpath(x['productname']).extract())
        item['pdesc'] = ''.join(response.xpath(x['description']).extract())
        item['pimage'] = ''.join(response.xpath(x['productimage']).extract())
        item['psize'] = '|'.join(response.xpath(x['size']).extract())
        item['psku'] = ''.join(response.xpath(x['productsku']).extract())
        item['pdate'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['pcolor'] = '|'.join(response.xpath(x['color']).extract())
        item['pprice'] = float(''.join(response.xpath(x['productprice']).extract()))
        item['pclass'] = 0
        yield item

    def _get_product_link(self,rep):
        data = rep.xpath('//*[@data-productid and @href]/@href').extract()
        if not data:
            raise "[SHIT] Something wrong"
            return []
        return data

    def parse(self, response):
        # net to get all product links one time
        links = self._get_product_link(response)
        for link in links:
            yield scrapy.Request('https://www.hollisterco.com'+str(link), callback=self.main_process)
        
