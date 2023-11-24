# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BangBrosItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass

class BangBros_Item(scrapy.Item):

    url = scrapy.Field()
    title = scrapy.Field()       
    release_date = scrapy.Field()      
    performers = scrapy.Field()       
    synopsis = scrapy.Field()        
    tags = scrapy.Field()      
    sub_side = scrapy.Field() 