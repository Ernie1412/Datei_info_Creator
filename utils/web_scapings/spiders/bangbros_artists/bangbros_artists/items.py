# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BangBrosArtistsItem(scrapy.Item):
    
    url = scrapy.Field()
    name = scrapy.Field()       
    sex = scrapy.Field()  
    image_urls = scrapy.Field()      
    image_name = scrapy.Field() 