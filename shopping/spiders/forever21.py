# -*- coding: utf-8 -*-
import scrapy
import json
from shopping.items import ShoppingItem
import sys
import datetime
import logging

class Forever21Spider(scrapy.Spider):
    name = "forever21"
    allowed_domains = ["forever21.com"]

    init_link = 'http://www.forever21.com/Product/Category.aspx?br=plus&category=plus-size-new-arrivals-tops'
    start_urls = (
        init_link,
    )

    def main_process(self, response):
        item = ShoppingItem()
        x_path = {
            'size': '//*[@id="ulProductSize"]/li/label/text()',
            'description': '//article[@class="ac-small"]',
            'color': '//*[@id="ulProductColor"]/li/a/img/@alt',
        }
        re_gex = {
            'productid': 'br_data.prod_id = "([^"]+)"',
            'productname': 'br_data.prod_name = "([^"]+)"',
            'productcat': 'br_data.cat = "([^"]+)"',
            'productsku': 'br_data.sku = \'([^\']+)\'',
            'productprice': 'br_data.price = \'([^\']+)\'',
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
        data = rep.xpath('//div[@class="product_grid c_list "]')
        if data:
            data = data[0]
        else:
            raise "[SHIT] Something wrong"
            return [],[]
        # check next page
        # check disable on next button
        disable_but = rep.xpath('//*[@class="p_prev"]/button[@title="next"]/@disabled').extract()
        next_page = rep.xpath('//*[@class="p_prev"]/button[@title="next"]/@onclick').extract()
        next_link = []
        if not disable_but:
            next_link = rep.url.split('?')[0] + next_page[0].split(';')[0][15:-1]
        return next_link, data.xpath('//div[@class="product_item gtm_prod"]/a/@href').extract()

    def parse(self, response):
        # net to get all product links one time
        next_link, links = self._get_product_link(response)
        for link in links:
            yield scrapy.Request(str(link), callback=self.main_process)
        
        # data = json.loads(response.body.decode('utf-8'))
        # if data.get('sections') and data.get('sections')[0].get('products'):
        #     for v in data.get('sections')[0].get('products'):
        #         yield scrapy.Request(v.get('pdpUrl'), callback=self.main_process)
        if next_link:
            yield scrapy.Request(str(next_link), callback=self.parse)
