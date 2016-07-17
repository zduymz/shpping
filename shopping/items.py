# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class TestingItem(scrapy.Item):
    mid = scrapy.Field()

class ShoppingItem(scrapy.Item):
    pid = scrapy.Field()
    pname = scrapy.Field()
    pdesc = scrapy.Field()
    pimage = scrapy.Field()
    psize = scrapy.Field()
    psku = scrapy.Field()
    pdate = scrapy.Field()
    pcolor = scrapy.Field()
    pprice = scrapy.Field()
    pgid = scrapy.Field()
    pclass = scrapy.Field()
