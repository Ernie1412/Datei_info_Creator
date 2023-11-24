import time
import os

from scrapy import Spider, Request
from scrapy import signals
from scrapy.signalmanager import dispatcher
from utils.web_scapings.spiders.bangbros.bangbros.items import BangBros_Item

class BangBrosNetworkSpider(Spider):
    name = 'bangbrosnetwork_spider'
    warte_schleife = None 
    bis_video=0  
    start_pages=0
    allowed_domains = ['www.bangbrosnetwork.com']
    start_urls = ['https://www.bangbrosnetwork.com/latest-videos']
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
                    }  
    start=False

    def parse(self, response):
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        if self.start:
            relative_urls = response.css('div.one-list-6uwu8z.e1fdx1xz1 a.one-list-hueuj4.e19uw93u1::attr(href)').extract()
            
            for relative_url in relative_urls:
                relative_url = relative_url.replace("/video/","/videos/") if "/video/" in relative_url else relative_url
                video_url = response.urljoin(relative_url)
                yield response.follow(video_url, callback = self.parse_video_page)

        self.start=True
        for index in range(self.start_pages, self.bis_video):
            next_page = f"https://www.bangbrosnetwork.com/latest-videos/page/{index}"
            if next_page is not None:
                self.stats_info["pages"]=index
                yield response.follow(next_page, callback = self.parse)


    def parse_video_page(self, response):        
        self.stats_info.update({
            "items_scraped": self.crawler.stats.get_value("item_scraped_count", 0),
            "pages_crawled": self.crawler.stats.get_value("pages_crawled", 0),        
            "error": self.crawler.stats.get_value("log_count/ERROR", 0),
                }   )        

        text = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        if text is None:
            time.sleep(1.5)
            # Wenn die Daten nicht vorhanden sind, kannst du erneut eine Anfrage senden
            yield Request(response.url, callback=self.parse_video_page)
        else:
            # Daten verarbeiten, wenn sie vorhanden sind
            pass

        performers = "\n".join(response.css('div.sc-1b6bgon-4.fWqGaG h2.sc-1b6bgon-0.llbToU a.sc-1b6bgon-8.YbRYu::text').extract())
        tags = ";".join(response.css('div.sc-vdkjux-1.eZmGdy a::text').extract())
        
        bangbros_item = BangBros_Item()        

        bangbros_item["url"] = response.url
        bangbros_item["title"] = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        bangbros_item["release_date"] = response.xpath("//div[@class='sc-1wa37oa-0 hCUrEB']//h2[@class='sc-1b6bgon-0 sc-1b6bgon-1 khrfTd']/text()").get()
        bangbros_item["performers"] = performers
        bangbros_item["synopsis"] = response.css('section[data-cy="description"] p.sc-1efjxte-1.iANaVe::text').get()
        bangbros_item["tags"] = tags
        bangbros_item["sub_side"] = response.css('a.sc-vdkjux-5.iyOHpd::text').get() 
        self.stats_info.update(bangbros_item)       

        yield bangbros_item 
        self.warte_schleife.put(self.stats_info) # items an den Qthread übergeben per Queue (Warte-Schleife) 

    def spider_closed(self, spider, reason):        
        # Hier eine asynchrone Verzögerung von 1 Sekunde einbauen
        #reactor.callLater(1, self.on_delayed_close, spider, reason)
        elapsed_time = self.crawler.stats.get_value("elapsed_time_seconds", 0)
        message= f"{spider.name} wurde beendet mit Grund: {reason}"
        self.warte_schleife.put(("ende",elapsed_time, message))