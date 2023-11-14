from PyQt6.QtCore import QDateTime, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QTableWidgetItem
from PyQt6 import QtWidgets
import time

from scrapy import signals, Spider, Request
from scrapy.signalmanager import dispatcher
from WebScapings.Spiders.bangbros.bangbros.items import BangBros_Item

from DBPages.DBPyQt_WebSides import DB_WebSide # daten in die datenbank speichern

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
        self.spidermonitor = spidermonitor 
        self.url: str = None   
        self.log_output: list = []
        self.load_spider_monitor_ui()        
        dispatcher.connect(self.handle_crawled, signal=signals.item_scraped)   
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
                
    
    def load_spider_monitor_ui(self): 
        self.spidermonitor.setWindowTitle("--- BangBrosSpider ---")
        zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.spidermonitor.lbl_time.setText(zeit)
        self.bis_video = self.Main.spinBox_bisVideo.value()
        self.spidermonitor.lbldatensatz_end.setText(f"von: {self.Main.spinBox_bisVideo.value()}")
        self.spidermonitor.show()
        self.spidermonitor.Btn_back.setEnabled(False)
        self.spidermonitor.Btn_back.clicked.connect(self.spidermonitor.close)
        QApplication.processEvents()

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
        self.url = response.url

        bangbros_item["url"] = response.url
        bangbros_item["title"] = response.css('h2.sc-1b6bgon-3.jAsNxx::text').get()
        bangbros_item["release_date"] = response.xpath("//div[@class='sc-1wa37oa-0 hCUrEB']//h2[@class='sc-1b6bgon-0 sc-1b6bgon-1 khrfTd']/text()").get()
        bangbros_item["performers"] = performers
        bangbros_item["synopsis"] = response.css('section[data-cy="description"] p.sc-1efjxte-1.iANaVe::text').get()
        bangbros_item["tags"] = tags
        bangbros_item["sub_side"] = response.css('a.sc-vdkjux-5.iyOHpd::text').get()
       

        yield bangbros_item

    
    def handle_crawled(self, item, response, spider):
        self.spidermonitor.Btn_break.setEnabled(True)
        self.spidermonitor.Btn_back.setEnabled(False)
        QApplication.processEvents()
        # Sende ein Signal mit den gecrawlten Daten
        crawler_stats = spider.crawler.stats.get_stats()
        crawled_info = {
            'url': response.url,
            'status': response.status,
            'stats': crawler_stats,
        }
        print(crawler_stats)
        dispatcher.send(signal=self.name + '_crawled', data=crawled_info)

    def set_url_tabelle(self) -> None:        
        zeile = self.spidermonitor.tblWdg_urls.currentRow()+1               
        self.spidermonitor.tblWdg_urls.setRowCount(zeile)
        self.spidermonitor.tblWdg_urls.setItem(zeile,0,QTableWidgetItem(self.url))
        self.spidermonitor.tblWdg_urls.update()
    
    def spider_closed(self, spider, reason):  
        self.spidermonitor.Btn_break.setEnabled(False)     
        self.spidermonitor.Btn_back.setEnabled(True)

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

    def __init__(self, MainWindow = None, *args, **kwargs):
        super(BangBrosNetworkSpider, self).__init__(*args, **kwargs)
        self.Main = MainWindow              
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
        self.load_spider_monitor_ui()
        QApplication.processEvents()
    
    def load_spider_monitor_ui(self):        
        self.spidermonitor.setWindowTitle("--- BangBrosSpider ---")
        zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.spidermonitor.lbl_time.setText(zeit)
        self.bis_video = self.Main.spinBox_bisVideo.value()
        self.spidermonitor.lbldatensatz_end.setText(f"von: {self.Main.spinBox_bisVideo.value()}")
        self.spidermonitor.show()
        self.spidermonitor.Btn_back.setEnabled(False)
        self.spidermonitor.Btn_back.clicked.connect(self.spidermonitor.close)

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


    def spider_closed(self, spider, reason):
        self.spidermonitor.Btn_back.setEnabled(True)
# class SpiderSignals(QObject):
#     crawled = pyqtSignal(dict)

# class SpiderMonitor(QtWidgets):
#     def __init__(self):
#         super(QtWidgets, self).__init__()
#         self.spider_signals = SpiderSignals()
#         self.spider_signals.crawled.connect(self.handle_crawled)

#     def handle_crawled(self, crawled_info):
#         # Aktualisiere die GUI mit den gecrawlten Daten
#         print("Crawled URL:", crawled_info['url'])
#         print("HTTP-Status:", crawled_info['status'])
#         print("Spider-Statistiken:", crawled_info['stats'])


# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     window = SpiderMonitor()

#     spider = BangBrosSpider()
#     dispatcher.connect(window.spider_signals.handle_crawled, signal=spider.name + '_crawled')

#     process = CrawlerProcess()
#     process.crawl(spider)
#     process.start()

#     window.show()
#     app.exec()
