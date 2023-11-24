from scrapy import Spider, Request
from scrapy import signals
from scrapy.signalmanager import dispatcher
from utils.web_scapings.spiders.bangbros_artists.bangbros_artists.items import BangBrosArtistsItem


class BangBrosArtistsSpider(Spider):
    name = "bangbros_artists_spider"
    warte_schleife = None 
    bis_video=0  
    start_pages=0
    stats_info = {"pages":0}
    allowed_domains = ["bangbros.com"]
    start_urls = ["https://bangbros.com/girls/sortby/alpha?gender=female"]

    start=True

    def parse(self, response):
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        bangbros_artists_item = BangBrosArtistsItem()
        if self.start:            
            relative_urls = response.css('div.one-list-6uwu8z.e1fdx1xz1 a.one-list-hueuj4.e19uw93u1::attr(href)').extract()
            names=response.css('div.one-list-6uwu8z.e1fdx1xz1 a.one-list-hueuj4.e19uw93u1::attr(href)').extract()
            image_urls=response.css('div.one-list-6uwu8z.e1fdx1xz1 a.one-list-hueuj4.e19uw93u1::attr(href)').extract()
            for relative_url,name,image_url in zip(relative_urls, names, image_urls):
                bangbros_artists_item["url"] = response.urljoin(relative_url)
                bangbros_artists_item["name"] = name
                bangbros_artists_item["sex"] = 1                
                id,_ = bangbros_artists_item["url"].replace("https://bangbros.com/model/","").rsplit("/",1) #https://bangbros.com/model/348811/aaliyah-grey
                bangbros_artists_item["image_url"] = response.urljoin(image_url)
                bangbros_artists_item["image"] = f"__artists_Images/{bangbros_artists_item['name']}/[BangBros]-{id}.jpg"