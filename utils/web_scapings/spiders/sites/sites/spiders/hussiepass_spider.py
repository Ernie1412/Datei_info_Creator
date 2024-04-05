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
import html

import dateparser

def call_process_queue(spider):
  spider.process_queue()

class HussiePassSpider(Spider):
    queue = Queue()     
    name = 'hussiepass'

    warte_schleife = None 
    bis_video=38 # last site 29-03-2024
    start_pages=1
    stats_info = {"pages":0}
    allowed_domains = ['seehimfuck.com']
    start_urls = [
        #'https://hussiepass.com',
        #'https://povpornstars.com',
        'https://seehimfuck.com',
    ]
    webside = start_urls[0]
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
                 }           
    start=False
    selector_map = {
        #'title': '//div[contains(@class,"videoDetails")]/h3/text()', # HussiePass
        'title': '//div[contains(@class,"videoDetails")]/h1/text()', # SeeHIMFuck
        'description': '//div[contains(@class,"videoDetails")]/p//text()',
        'date': '//div[contains(@class,"videoInfo")]/p/span[contains(text(),"Added")]/following-sibling::text()',
        "runtime": '//div[contains(@class,"videoInfo")]/p[contains(text(),"Min")]//text()',
        # 'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href,"/categories/")]/text()',
        'external_id': '.*\\/(.*?)\\.html',
        # 'trailer': '//script[contains(text(),"video_content")]',
        'pagination': '/categories/movies/%s/latest/'
    }
    
    def __init__(self):        
        thread = Thread(target=call_process_queue, args=(self,))
        thread.start()
        
    def cleanup_text(self, text, trash_words=None):
        if trash_words is None:
            trash_words = []
        text = html.unescape(text)
        
        for trash in trash_words:            
            if trash in text:                
                text = text.replace(trash, '')
        return text.strip()
    
    def cleanup_runtime(self, text):
        text = text.replace('\xa0', ' ')
        match = re.search(r'(\d+) Min', text)
        if match:
            hours = int(match.group(1)) // 60 
            mins = int(match.group(1)) % 60
            minutes = f"{hours:02d}:{mins:02d}:00"
        else:
            minutes = "00:00:00"            
        return minutes

        
    def get_selector_map(self, attr=None):
        if hasattr(self, 'selector_map'):
            if attr is None:
                return self.selector_map
            if attr not in self.selector_map:
                raise AttributeError(f'{attr} missing from selector map')
            return self.selector_map[attr]
        raise NotImplementedError('selector map missing')  
    
    # def get_scenes(self, response):        
    #     scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()        
    #     for scene_url in scenes:            
    #         print(scene_url) 
    #         if re.search(self.get_selector_map('external_id'), scene_url):           
    #             yield response.follow(scene_url, callback=self.parse_video_page)

    def parse(self, response):        
      
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        if self.start:            
            #self.get_scenes(response)
            scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()            
            for scene in scenes:                
                print(scene)                
                yield response.follow(scene, callback=self.parse_video_page)

        self.start=True
        for page_number in range(self.start_pages, self.bis_video):
            pagination_path = self.get_selector_map('pagination') % page_number
            next_page = f"{self.webside}{pagination_path}"                        
            if next_page is not None:                 
                self.stats_info["pages"]=page_number
                yield response.follow(next_page, callback=self.parse) 

    # def get_next_page_url(self, base, page):
    #     if 'hussiepass' in base or 'seehimfuck' in base:
    #         selector = '/categories/movies/%s/latest/'
    #     if 'povpornstars' in base:
    #         selector = '/tour/categories/movies/%s/latest/'
    #     return self.format_url(base, selector % page) 

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
        trash_words = ['📏','➕','☝🏾','😊','👩‍🎤']
        performers = self.cleanup_text(performers,trash_words)

        tags_xpath = self.get_selector_map('tags')
        tags = ";".join(response.xpath(tags_xpath).getall())
        
        date = self.datum_umwandeln(response.xpath(self.get_selector_map('date')).get().strip(), '%Y-%m-%d')

        runtime_raw = response.xpath(self.get_selector_map('runtime')).get()
        runtime = self.cleanup_runtime(runtime_raw)

        scene_item = SceneItem()        

        scene_item["studio"] = "SeeHIMFuck"
        scene_item["url"] = response.url
        scene_item["title"] = response.xpath(self.get_selector_map('title')).get()
        scene_item["release_date"] = date
        scene_item["performers"] = performers.strip()
        scene_item["synopsis"] = response.xpath(self.get_selector_map('description')).get().strip()
        scene_item["tags"] = tags        
        scene_item["during"] = runtime
        self.stats_info.update(scene_item) 

        self.queue.put(scene_item)
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