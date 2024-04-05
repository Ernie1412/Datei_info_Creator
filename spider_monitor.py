from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QApplication, QTableWidgetItem
from PyQt6.QtCore import QThread, QDateTime


from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings



import sys
from threading import Semaphore
from multiprocessing import Process, Manager

# Pfade einrichten
# current_file_path = Path(__file__).resolve()
# project_root = current_file_path.parents[2]  # Zwei Verzeichnisse über dem aktuellen Skript
# sys.path.append(str(project_root))


from utils.helpers.umwandeln import from_classname_to_import
from config import SPIDER_MONITOR_UI

class SpiderMonitor(QDialog):
    def __init__(self, spider=None, parent=None):
        super(SpiderMonitor, self).__init__(parent)
        self.prozess = None
        self.warte_schleife = Manager().Queue()
        self.ausgaben_thread = AusgabenThread(self)
        uic.loadUi(SPIDER_MONITOR_UI, self)
        self.Main = parent 
        #self.spider_class_name = "utils.web_scapings.spiders.bangbros.bangbros.spiders.bangbrosnetwork_spider.BangBrosNetworkSpider"
        self.spider_class_name = "utils.web_scapings.spiders.bangbros.bangbros.spiders.bangbros_spider.BangBrosSpider" 
        _, class_name = self.spider_class_name.rsplit('.', 1)
        window_width=self.width()
        m=int(window_width/3.8)        
        self.setWindowTitle(f"{class_name: ^{m}}")
        zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.lbl_time.setText(zeit)
        self.bis_video = 10 #self.Main.spinBox_bisVideo.value()
        self.start_pages = 1 #self.Main.spinBox_vonVideo.value()
        self.lbldatensatz_end.setText(f"von: {self.bis_video}")
        self.lbl_datensatz.setText(f"{self.start_pages}")
        self.show()        
        self.Btn_back.clicked.connect(self.close)
        self.Btn_break.clicked.connect(self.spider_stop) 
        self.Btn_start.clicked.connect(self.spider_start)
       

    def set_url_tabelle(self) -> None:        
        zeile = self.tblWdg_urls.currentRow()+1               
        self.tblWdg_urls.setRowCount(zeile)
        self.tblWdg_urls.setItem(zeile,0,QTableWidgetItem(self.url))
        self.tblWdg_urls.update()

    
    def spider_closed(self, spider, reason):  
        self.Btn_break.setEnabled(False)     
        self.Btn_back.setEnabled(True)
    
    def spider_start(self):
        self.Btn_break.setEnabled(True)     
        self.Btn_back.setEnabled(False)
        self.prozess = Process(target=crawl_run, args=(self.warte_schleife, self.spider_class_name, self.bis_video,  self.start_pages))        
        self.prozess.start()
        self.ausgaben_thread.start()

    def spider_stop(self):
        self.Btn_break.setEnabled(False)     
        self.Btn_back.setEnabled(True)
        if self.prozess and self.prozess.is_alive():
            text=self.lbl_message.text()
            self.lbl_message.setText(f"{text} ... Spider gestoppt !")
            self.ausgaben_thread.wait_for_spider_end()
            self.ausgaben_thread.quit()
            self.prozess.terminate()
        

def crawl_run(warte_schleife, spider_class_name, bis_video, start_pages):        
    spider_class_pipeline = from_classname_to_import(spider_class_name)
    module_path, class_name = spider_class_name.rsplit('.', 1)        
    parts = module_path.split('.')
    settings_module = '.'.join(parts[:-2])+'.settings'        
    # Alternative Settings-Instanz erstellen
    custom_settings = Settings()
    custom_settings.setmodule(settings_module)          


    try:
        process = CrawlerProcess(settings=custom_settings)
        process.crawl(spider_class_pipeline, warte_schleife=warte_schleife, bis_video=bis_video,  start_pages=start_pages)
        process.start()
    except Exception as e:
        print(f"Error during crawling: {e}")



class AusgabenThread(QThread):
    def __init__(self, gui):
        super(AusgabenThread, self).__init__()
        self.gui = gui
        self.stop_event = Semaphore(0)  # Semaphore für das Beenden des Threads
        self.abort: bool = False  # Initialisiere self.abort

    def run(self) -> None: 
        self.abort = True               
        neu=0
        update=0
        self.gui.lbl_update.setText(f"{update}")
        self.gui.lbl_neu.setText(f"{neu}")
        while self.abort:
            if not self.gui.warte_schleife.empty():
                record = self.gui.warte_schleife.get()                 
                if isinstance(record, dict):                                      
                    if record.get("items_scraped"):
                        self.gui.lbl_datensatz.setText(f"{record['items_scraped']}")                    
                        self.gui.lbl_pages.setText(f"{record['pages']}")
                    if record.get("error"):
                        self.gui.lbl_error.setText(record["error"])                        
                    if record.get("url"):
                        zeile=self.gui.tblWdg_urls.rowCount()
                        self.gui.tblWdg_urls.setRowCount(zeile+1)                    
                        self.gui.tblWdg_urls.setItem(zeile, 0, QTableWidgetItem(record["url"]))                
                    if record.get("neu"):
                        neu += 1
                        self.gui.lbl_neu.setText(f"{neu}")
                    if record.get("neu") is False: 
                        update +=1
                        self.gui.lbl_update.setText(f"{update}")
                if isinstance(record, tuple):                    
                    self.gui.lbl_counter.setText(f"{record[1]}")
                    self.gui.lbl_message.setText(f"{record[2]}")
                    self.stop_event.release()  # Signalisiere das Ende des Spiders
                    self.stop()  # Beende den Thread

    def wait_for_spider_end(self):
        self.stop_event.acquire()  # Warte, bis das Semaphore freigegeben wird

    def stop(self):
        self.abort = False        
        self.gui.spider_stop()
        

if __name__ == '__main__':   
    app, SpiderWindow =(QApplication(sys.argv), SpiderMonitor())
    SpiderWindow.show()      
    sys.exit(app.exec())