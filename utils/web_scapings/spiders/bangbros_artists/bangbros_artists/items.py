# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BangBrosArtistsItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()       
    sex = scrapy.Field()  
    image_url = scrapy.Field()      
    image = scrapy.Field() 