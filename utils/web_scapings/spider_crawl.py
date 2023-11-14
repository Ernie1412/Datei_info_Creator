from scrapy.crawler import CrawlerProcess
import sys
import importlib
from pathlib import Path
from utils.database_settings.database_for_settings import Webside_Settings


# Aktuelles Verzeichnis von spider_crawl.py
current_folder = Path(__file__).resolve().parent
# Übergeordnetes Verzeichnis (Datei_Info_Creator/WebScapings)
project_folder = current_folder.parent
# Füge das übergeordnete Verzeichnis zum Python-Pfad hinzu
sys.path.append(str(project_folder))

class SpiderLoader:
    def __init__(self, spider_class_name: str, MainWindow, spidermonitor):
        self.Main = MainWindow
        self.spidermonitor = spidermonitor
        self.spider_class_name = spider_class_name
    
    def spider_crawler(self):                
        module_path, class_name = self.spider_class_name.rsplit('.', 1)
        module = importlib.import_module(module_path)
        spider_class = getattr(module, class_name)        

        process = CrawlerProcess()
        process.crawl(spider_class, spidermonitor=self.spidermonitor, MainWindow=self.Main)
        process.start()