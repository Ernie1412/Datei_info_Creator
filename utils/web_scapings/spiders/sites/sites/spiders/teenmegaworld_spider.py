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


def call_process_queue(spider):
  spider.process_queue()

class TeenMegaWorldSpider(Spider):
    name = 'TeenMegaWorld'
    network = 'teenmegaworld'
    queue = Queue()   
    warte_schleife = None 
    bis_video=259
    start_pages=2
    stats_info = {"pages":0}
    allowed_domains = ['teenmegaworld.net']
    start_urls = [
        'https://teenmegaworld.net',
        # 'http://rawcouples.com/',
        # 'http://anal-angels.com',
        # 'http://anal-beauty.com',
        # 'http://beauty4k.com',
        # 'http://beauty-angels.com',
        # 'http://creampie-angels.com',
        # 'http://dirty-coach.com',
        # 'http://dirty-doctor.com',
        # 'http://firstbgg.com',
        # 'http://fuckstudies.com',
        # 'http://gag-n-gape.com',
        # 'http://lollyhardcore.com',
        # 'http://noboring.com',
        # 'http://nubilegirlshd.com',
        # 'http://old-n-young.com',
        # 'http://soloteengirls.net',
        # 'http://teensexmania.com',
        # 'http://trickymasseur.com',
        # 'http://x-angels.com',
        # 'http://teensexmovs.com',
    ]
    webside = start_urls[0]
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
                 }           
    start=False
    selector_map = {
        'title': "//div[contains(@class,'video-heading')]/h1[@id='video-title']/text()",
        'description': "//div[@id='video-description']/p[@class='video-description-text']/text()",
        'date': "//span[@class='video-info-date d-flex']/text()[normalize-space()]",
        'date_formats': ['%B %d, %Y'],
        'image': '//deo-video/@poster | //video/@poster | //meta[@property="og:image"]/@content',
        'performers': "//span[contains(@class,'video-actor-list')]/a[contains(@class,'video-actor-link')]/text()",
        'tags': "//div[contains(@class,'video-tag-list')]/a[@class='video-tag-link']/text()",
        'external_id': r'trailers/(.+)\.html',
        'trailer': '//source/@src',
        'pagination': '/categories/movies_%s_d.html',
        'subsite': "//a[@class='video-site-link btn btn-ghost btn--rounded']/text()",
        'during': "//span[@class='video-info-time d-flex']/text()[normalize-space()]",
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
    
    # def get_scenes(self, response):        
    #     scenes = response.xpath("//a[contains(@class,'Link SceneThumb-SceneInfo-SceneTitle-Link')]") 
    #     dates = response.xpath("//span[@class='Text SceneThumb-Length-Text']")
    #     meta = {}       
    #     for scene, date in zip(scenes, dates):
    #         meta['date'] = date.xpath('./text()').get()            
    #         scene_url = scene.xpath('./@href').get()
    #         yield response.follow(scene_url, callback=self.parse_video_page, meta=meta)

    def parse(self, response):        
      
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        if self.start:            
            #self.get_scenes(response)
            scenes = response.xpath('//h2[@class="thumb__title"]/a/@href').getall()
            for scene in scenes:
                print(scene)
                yield Request(url=scene, callback=self.parse_scene)

        self.start=True
        for page_number in range(self.start_pages, self.bis_video):
            pagination_path = self.get_selector_map('pagination') % page_number
            next_page = f"{self.webside}{pagination_path}"                        
            if next_page is not None:
                print(next_page) 
                self.stats_info["pages"]=page_number
                yield response.follow(next_page, callback=self.parse)  

    def parse_scene(self, response): 
        
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

        date_str = response.xpath(self.get_selector_map('date')).get().replace('\n', '').strip()
        date = self.datum_umwandeln(date_str, date_format='%B %d, %Y')

        time_str = response.xpath(self.get_selector_map('during')).get()
        time_formatted = self.cleanup_runtime(time_str) if time_str else None
        
        scene_item = SceneItem() 

        scene_item["studio"] = "TMW"
        scene_item["url"] = response.url
        scene_item["title"] = scene_title
        scene_item["release_date"] = date
        scene_item["performers"] = performers
        scene_item["synopsis"] = response.xpath(self.get_selector_map('description')).get().strip()
        scene_item["tags"] = tags        
        scene_item["during"] = None
        scene_item["scene_code"] = None
        scene_item["director"] = None
        scene_item["sub_site"] = response.xpath(self.get_selector_map('subsite')).get()
        scene_item["during"] = time_formatted

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

    def cleanup_runtime(self, text):
        text = text.replace('\n', '')
        match = re.search(r'(\d+) min', text)
        if match:
            hours = int(match.group(1)) // 60 
            mins = int(match.group(1)) % 60
            minutes = f"{hours:02d}:{mins:02d}:00"
        else:
            minutes = "00:00:00"            
        return minutes

    def datum_umwandeln(self, date_str:str, date_format: str) -> str:
        try:
            date_obj = datetime.strptime(date_str, date_format)
        except ValueError:
            return None    
        # Datumsobjekt in das gewünschte Format umwandeln        
        return date_obj.strftime('%Y:%m:%d %H:%M:%S')
    
    def format_link(self, response, link):
        return self.format_url(response.url, link)