import time

from scrapy import Spider, Request
from utils.web_scapings.spiders.bangbros.bangbros.items import BangBros_Item

class MonsterOfCockSpider(Spider):
    name = 'monsterofcock_spider'
    allowed_domains = ['members.monstersofcock.com']
    start_urls = ['https://members.monstersofcock.com/']
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
        'FEEDS': {         
                'bangbros.json': {'format': 'json', 'overwrite': True},
                 }    } # automatisch in json speichern
    
    
class BangBrosSpider(Spider):
    name = 'bangbros_spider'
    allowed_domains = ['bangbros.com']
    start_urls = ['https://bangbros.com/videos/page/1']
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
        'FEEDS': {         
                'bangbros.json': {'format': 'json', 'overwrite': True},
                 }    } # automatisch in json speichern

    def __init__(self, MainWindow, spidermonitor, *args, **kwargs):
        super(BangBrosSpider, self).__init__(*args, **kwargs)
        self.Main = MainWindow 
        self.url: str = None   
        self.log_output: list = []

    def parse(self, response):
        relative_urls = response.css('div.one-list-6uwu8z.e1fdx1xz1 a.one-list-hueuj4.e19uw93u1::attr(href)').extract()
        # Logge die extrahierten Daten        
        if response.status != 200:
            self.log_output.append(f"Error: {response.status} - {response.text}")

        for relative_url in relative_urls:
            video_url = "https://bangbros.com" + relative_url
            yield response.follow(video_url, callback = self.parse_video_page)
        
        for index in range(1,self.bis_video+1):
            next_page = f"https://bangbros.com/videos/page/{index}"
            self.index = next
            if next_page is not None:
                yield response.follow(next_page, callback = self.parse)


    def parse_video_page(self, response):
        text = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        if text is None:
            time.sleep(1)
            # Wenn die Daten nicht vorhanden sind, kannst du erneut eine Anfrage senden
            yield Request(response.url, callback=self.parse_video_page)
        else:
            # Daten verarbeiten, wenn sie vorhanden sind
            pass

        performers = ", ".join(response.css('div.sc-1b6bgon-4.fWqGaG h2.sc-1b6bgon-0.llbToU a.sc-1b6bgon-8.YbRYu::text').extract())
        tags = ";".join(response.css('div.sc-vdkjux-1.eZmGdy a::text').extract())
        bangbros_item = BangBros_Item()        

        bangbros_item["url"] = response.url
        bangbros_item["title"] = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        bangbros_item["release_date"] = response.xpath("//div[@class='sc-1wa37oa-0 hCUrEB']//h2[@class='sc-1b6bgon-0 sc-1b6bgon-1 khrfTd']/text()").get()
        bangbros_item["performers"] = performers
        bangbros_item["synopsis"] = response.css('section[data-cy="description"] p.sc-1efjxte-1.iANaVe::text').get()
        bangbros_item["tags"] = tags
        bangbros_item["sub_side"] = response.css('a.sc-vdkjux-5.iyOHpd::text').get()       

        yield bangbros_item


class BangBrosNetworkSpider(Spider):
    name = 'bangbros_spider'
    allowed_domains = ['www.bangbrosnetwork.com']
    start_urls = ['https://www.bangbrosnetwork/videos/page/1']
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
        'FEEDS': {         
                'bangbrosnetwork.json': {'format': 'json', 'overwrite': True},
                }    } # automatisch in json speichern      
    


    def parse(self, response):
        relative_urls = response.css('div.one-list-6uwu8z.e1fdx1xz1 a.one-list-hueuj4.e19uw93u1::attr(href)').extract()

        for relative_url in relative_urls:
            video_url = "https://www.bangbrosnetwork.com" + relative_url
            yield response.follow(video_url, callback = self.parse_video_page)
        
        for index in range(1,self.bis_video+1):
            next_page = f"https://www.bangbrosnetwork.com/videos/page/{index}"
            if next_page is not None:
                yield response.follow(next_page, callback = self.parse)


    def parse_video_page(self, response):
        text = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        if text is None:
            time.sleep(1)
            # Wenn die Daten nicht vorhanden sind, kannst du erneut eine Anfrage senden
            yield Request(response.url, callback=self.parse_video_page)
        else:
            # Daten verarbeiten, wenn sie vorhanden sind
            pass

        performers = ", ".join(response.css('div.sc-1b6bgon-4.fWqGaG h2.sc-1b6bgon-0.llbToU a.sc-1b6bgon-8.YbRYu::text').extract())
        tags = ";".join(response.css('div.sc-vdkjux-1.eZmGdy a::text').extract())
        bangbros_item = BangBros_Item()

        bangbros_item["url"] = response.url
        bangbros_item["title"] = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        bangbros_item["release_date"] = response.xpath("//div[@class='sc-1wa37oa-0 hCUrEB']//h2[@class='sc-1b6bgon-0 sc-1b6bgon-1 khrfTd']/text()").get()
        bangbros_item["performers"] = performers
        bangbros_item["synopsis"] = response.css('section[data-cy="description"] p.sc-1efjxte-1.iANaVe::text').get()
        bangbros_item["tags"] = tags
        bangbros_item["sub_side"] = response.css('a.sc-vdkjux-5.iyOHpd::text').get()
            
        yield bangbros_item

class Pipeline():

    @classmethod
    def add_link(cls, link):
        if link.startswith("https://bangbros.com/"):
            bangbrosnetwork = link.replace("https://bangbros.com/","https://www.bangbrosnetwork.com/").replace("/video/","/videos/")
            links = link + "\n" + bangbrosnetwork
        if link.startswith("https://www.bangbrosnetwork.com/"):
            bangbros = link.replace("https://www.bangbrosnetwork.com/","https://bangbros.com/").replace("/videos/","/video/")
            links = link + "\n" + bangbros
        return links 
    
    def movie_distr(cls, studio, jahr):
        return "BangProductions" if jahr < 2017 else "GirlFriendsFilms"
