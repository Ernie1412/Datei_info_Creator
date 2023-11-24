import time

from scrapy import Spider, Request
from scrapy import signals
from scrapy.signalmanager import dispatcher
from utils.web_scapings.spiders.bangbros.bangbros.items import BangBros_Item


class MonsterOfCockSpider(Spider):
    name = 'monsterofcock_spider'
    warte_schleife = None 
    bis_video=0  
    start_pages=0
    allowed_domains = ['members.monstersofcock.com']
    start_urls = ['https://members.monstersofcock.com/']
    custom_settings = {
        'DOWNLOAD_MAX': 3,  # Maximale Anzahl der erlaubten Anfragen pro URL
        'RETRY_TIMES': 5,  # Maximale Anzahl der Wiederholungsversuche bei Fehlern
            }  
    start=False