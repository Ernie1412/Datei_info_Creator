import time

from scrapy import Spider, Request
from scrapy import signals
from utils.web_scapings.spiders.sites.sites.pipelines import MyDatabasePipeline
from scrapy.signalmanager import dispatcher
from utils.web_scapings.spiders.sites.sites.items import SceneItem
from threading import Thread 
from queue import Queue
import re


def call_process_queue(spider):
  spider.process_queue()

class BangBrosSpider(Spider):
    queue = Queue()     
    name = 'bangbros_spider'
    warte_schleife = None 
    bis_video=2
    start_pages=1
    stats_info = {"pages":0}
    allowed_domains = ['bangbros.com']
    start_urls = ['https://bangbros.com/']
    webside = start_urls[0]
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
                 }           
    start=False
    def __init__(self):
        # Thread erst hier starten 
        thread = Thread(target=call_process_queue, args=(self,))
        thread.start()

        selector_map = {
            'title': '//h1[@class="title"]/text()',
            'description': '//div[@class="text-desc"]/p/text()',
            'date': '',
            'image': '//img[@class="player-preview"]/@src',
            'performers': '//ul[contains(text(), "Models")]/li/a/text()',
            'tags': '//ul[@class="list-inline"]/li/a[contains(@href, "/tags/")]/text()',
            'external_id': r'.*-(\d+)/$',     
            'pagination': '/latest-updates/%s/',
            'during': '//ul[@class="list-inline"]/li[2]/span/text()',
            'pagination': '/categories/movies/%s/latest/'
    }
    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb-content"]')
        for scene in scenes:
            meta = {}
            date = scene.xpath('./div/span[@class="thumb-added"]/text()')
            if date:
                meta['date'] = self.parse_date(date.get(), date_formats=['%b %d, %Y']).isoformat().replace("-", ":")+"00:00:00"
            else:
                meta['date'] = self.parse_date('today').isoformat().replace("-", ":")+"00:00:00"
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
    def parse(self, response):        
      
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        if self.start:            
            relative_urls = response.css('div.one-list-6uwu8z.e1fdx1xz1 a.one-list-hueuj4.e19uw93u1::attr(href)').extract()
            # Logge die extrahierten Daten
            for relative_url in relative_urls:
                relative_url = relative_url.replace("/videos/","/video/") if "/videos/" in relative_url else relative_url 
                video_url = response.urljoin(relative_url)
                yield response.follow(video_url, callback = self.parse_video_page) 

        self.start=True
        for index in range(self.start_pages, self.bis_video):
            next_page = f"{self.webside}{index}"            
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
        
        bangbros_item = SceneItem()        

        bangbros_item["studio"] = "BangBros"
        bangbros_item["url"] = response.url
        bangbros_item["title"] = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        bangbros_item["release_date"] = response.xpath("//div[@class='sc-1wa37oa-0 hCUrEB']//h2[@class='sc-1b6bgon-0 sc-1b6bgon-1 khrfTd']/text()").get()
        bangbros_item["performers"] = performers
        bangbros_item["synopsis"] = response.css('section[data-cy="description"] p.sc-1efjxte-1.iANaVe::text').get()
        bangbros_item["tags"] = tags
        bangbros_item["sub_side"] = response.css('a.sc-vdkjux-5.iyOHpd::text').get() 
        self.stats_info.update(bangbros_item) 

        self.queue.put(bangbros_item)
        #yield bangbros_item 
        #self.warte_schleife.put(self.stats_info) # items an den Qthread übergeben per Queue (Warte-Schleife) 

    def spider_closed(self, spider, reason):        
        # Hier eine asynchrone Verzögerung von 1 Sekunde einbauen
        #reactor.callLater(1, self.on_delayed_close, spider, reason)
        elapsed_time = self.crawler.stats.get_value("elapsed_time_seconds", 0)
        message= f"{spider.name} wurde beendet mit Grund: {reason}"
        #self.warte_schleife.put(("ende",elapsed_time, message))
    
    def process_queue(self):
        pipeline = MyDatabasePipeline()
        while True:
            bangbros_item = self.queue.get()
            pipeline.process_item(bangbros_item, spider=self)