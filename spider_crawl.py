
import sys
import logging
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerProcess
#from utils.web_scapings.spiders.bangbros.bangbros.spiders.bangbros_spider import BangBrosSpider
#from utils.web_scapings.spiders.firstanalquest_video.firstanalquest_video.spiders.firstanalquest import FirstAnalQuestSpider
from utils.web_scapings.spiders.sites.sites.spiders.teenmegaworld_spider import TeenMegaWorldSpider
from queue import Queue

LOG_FILE = "scrapy_output.log"
queue = Queue()
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Initialisierung des Crawler-Prozesses mit angegebenem Loglevel
crawler = CrawlerProcess(settings={
    'LOG_FILE': LOG_FILE,        
    'BOT_NAME': 'hardx', 
    'ROBOTSTXT_OBEY': False,
    'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    'SPIDER_MODULES': ['utils.web_scapings.spiders.sites.sites.spiders'],
    'NEWSPIDER_MODULE': 'utils.web_scapings.spiders.sites.sites.spiders',
    'LOG_LEVEL': 'INFO',  # Loglevel auf INFO setzen
    
    'DEFAULT_HEADERS': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'},
    'ITEM_PIPELINES' : {      
        'utils.web_scapings.spiders.sites.sites.pipelines.MyDatabasePipeline': 800
        }  # Protokolldatei festlegen
})


# Crawl ausführen

crawler.crawl(TeenMegaWorldSpider)
crawler.start()

# Schließe die Protokolldatei
sys.stdout.close()
sys.stderr.close()


