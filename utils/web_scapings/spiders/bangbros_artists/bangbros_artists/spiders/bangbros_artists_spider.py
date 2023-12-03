from scrapy import Spider, Request
from scrapy import signals
from scrapy.signalmanager import dispatcher
from bangbros_artists.items import BangBrosArtistsItem
#utils.web_scapings.spiders.bangbros_artists.

class BangBrosArtistsSpider(Spider):
    name = "bangbros_artists_spider"
    warte_schleife = None 
    bis_video=1  
    start_pages=2
    stats_info = {"pages":0}
    allowed_domains = ["www.bangbrosnetwork.com"]
    start_urls = ["https://www.bangbrosnetwork.com/latest-girls/page/1"]

    start=False

    def parse(self, response):
        #dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        if self.start:
            relative_urls = response.css('a.one-list-hueuj4.e19uw93u1::attr(href)').extract()
            namen=response.css('a.one-list-hueuj4.e19uw93u1::attr(title)').extract()
            image_urls_extract=response.css('img.one-list-q4dzvk.esqduzl0::attr(src)').extract()
            self.log(f'Found {len(image_urls_extract)} image URLs: {image_urls_extract}')

            for relative_url, name, image_url in zip(relative_urls, namen, image_urls_extract):
                item = BangBrosArtistsItem()
                item["url"] = response.urljoin(relative_url)
                item["name"] = name
                item["sex"] = 1
                item["image_urls"] = [image_url]
                id,_ = relative_url.replace("/model/","").rsplit("/",1) #/model/{348811}/aaliyah-grey
                item["image_name"] = f"[BangBros]-{id}"
                yield item   

        self.start=True
        for index in range(1, 3): # page 1 und 2
            next_page = f"https://www.bangbrosnetwork.com/latest-girls/page/{index}"        
            if next_page is not None: 
                #self.stats_info["pages"]=index
                yield response.follow(next_page, callback = self.parse)