import time

from scrapy import Spider, Request
from scrapy import signals
from utils.web_scapings.spiders.sites.sites.pipelines import MyDatabasePipeline
from scrapy.signalmanager import dispatcher
from utils.web_scapings.spiders.sites.sites.items import SceneItem
from threading import Thread 
from queue import Queue
import re
from datetime import datetime

import dateparser

def call_process_queue(spider):
  spider.process_queue()

class FirstAnalQuestSpider(Spider):
    queue = Queue()     
    name = 'firstanalquestspider'
    warte_schleife = None 
    bis_video=22
    start_pages=1
    stats_info = {"pages":0}
    allowed_domains = ['www.firstanalquest.com']
    start_urls = ['http://www.firstanalquest.com']
    webside = start_urls[0]
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
                 }           
    start=False
    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//div[@class="text-desc"]/p/text()',
        'date': '',
        'image': '//img[@class="player-preview"]/@src',
        'performers': '//ul[contains(text(), "Models")]/li/a/text()',
        'tags': '//ul[@class="list-inline"]/li/a[contains(@href, "/tags/")]/text()',
        'external_id': r'.*-(\d+)/$',     
        'pagination': '/latest-updates/%s/',
        'subside': '',
        'during': '//ul[@class="list-inline"]/li[2]/span/text()'
        }
    
    def __init__(self):        
        thread = Thread(target=call_process_queue, args=(self,))
        thread.start()  
        
    def get_selector_map(self, attr=None):
        if hasattr(self, 'selector_map'):
            if attr is None:
                return self.selector_map
            if attr not in self.selector_map:
                raise AttributeError(f'{attr} missing from selector map')
            return self.selector_map[attr]
        raise NotImplementedError('selector map missing')  
    
    def get_scenes(self, response):        
        scenes = response.xpath('//div[@class="thumb-content"]')
        print(scenes)
        for scene in scenes:
            meta = {}
            date = scene.xpath('./div/span[@class="thumb-added"]/text()')
            if date: 
                date_format = self.datum_umwandeln(date.get(), '%b %d, %Y')               
                meta['date'] = date_format   
            scene_url = scene.xpath('./a/@href').get()
            yield response.follow(scene_url, callback=self.parse_video_page, meta=meta)

    def parse(self, response):        
      
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        if self.start:            
            #self.get_scenes(response)
            scenes = response.xpath('//div[@class="thumb-content"]')            
            for scene in scenes:
                meta = {}
                date = scene.xpath('./div/span[@class="thumb-added"]/text()')
                if date: 
                    date_format = self.datum_umwandeln(date.get(), date_format='%b %d, %Y')               
                    meta['date'] = date_format   
                scene_url = scene.xpath('./a/@href').get()
                print(scene_url)
                print(date_format)
                yield response.follow(scene_url, callback=self.parse_video_page, meta=meta)

        self.start=True
        for page_number in range(self.start_pages, self.bis_video):
            pagination_path = self.get_selector_map('pagination') % page_number
            next_page = f"{self.website}{pagination_path}"                        
            if next_page is not None:
                print(next_page) 
                self.stats_info["pages"]=page_number
                yield response.follow(next_page, callback=self.parse)  

    def parse_video_page(self, response): 
        meta = response.meta
        self.stats_info.update({
            "items_scraped": self.crawler.stats.get_value("item_scraped_count", 0),
            "pages_crawled": self.crawler.stats.get_value("pages_crawled", 0),        
            "error": self.crawler.stats.get_value("log_count/ERROR", 0),
                }   )        

        scene_title = response.xpath(self.get_selector_map('title')).get()
        if scene_title is None:
            time.sleep(1.5)
            # Wenn die Daten nicht vorhanden sind, kannst du erneut eine Anfrage senden
            yield Request(response.url, callback=self.parse_video_page)        

        performers = "\n".join(response.xpath(self.get_selector_map('performers')).getall())
        tags_xpath = self.get_selector_map('tags')
        tags = ";".join(response.xpath(tags_xpath).getall())
        
        firstanalquest_item = SceneItem() 

        firstanalquest_item["studio"] = "FirstAnalQuest"
        firstanalquest_item["url"] = response.url
        firstanalquest_item["title"] = response.xpath(self.get_selector_map('title')).get()
        firstanalquest_item["release_date"] = meta.get('date')
        firstanalquest_item["performers"] = performers
        firstanalquest_item["synopsis"] = response.xpath(self.get_selector_map('description')).get().strip()
        firstanalquest_item["tags"] = tags        
        firstanalquest_item["during"] = f"00:{response.xpath(self.get_selector_map('during')).get()}"
        self.stats_info.update(firstanalquest_item) 

        self.queue.put(firstanalquest_item)
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

    def datum_umwandeln(self, date_str:str, date_format: str) -> str:
        try:
            date_obj = datetime.strptime(date_str, date_format)
        except ValueError:
            return None    
        # Datumsobjekt in das gewünschte Format umwandeln        
        return date_obj.strftime('%Y:%m:%d %H:%M:%S')
    
    def format_link(self, response, link):
        return self.format_url(response.url, link)