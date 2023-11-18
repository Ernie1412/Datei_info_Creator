    def load_spider_monitor_ui(self): 
        self.spidermonitor.setWindowTitle(f"--- {titel} ---")
        zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.spidermonitor.lbl_time.setText(zeit)
        self.bis_video = self.Main.spinBox_bisVideo.value()
        self.spidermonitor.lbldatensatz_end.setText(f"von: {self.Main.spinBox_bisVideo.value()}")
        self.spidermonitor.show()
        self.spidermonitor.Btn_back.setEnabled(False)
        self.spidermonitor.Btn_back.clicked.connect(self.spidermonitor.close)
        

    def handle_crawled(self, item, response, spider):
        self.spidermonitor.Btn_break.setEnabled(True)
        self.spidermonitor.Btn_back.setEnabled(False)
        
        # Sende ein Signal mit den gecrawlten Daten
        crawler_stats = spider.crawler.stats.get_stats()
        crawled_info = {
            'url': response.url,
            'status': response.status,
            'stats': crawler_stats,
        }
       

    def set_url_tabelle(self) -> None:        
        zeile = self.spidermonitor.tblWdg_urls.currentRow()+1               
        self.spidermonitor.tblWdg_urls.setRowCount(zeile)
        self.spidermonitor.tblWdg_urls.setItem(zeile,0,QTableWidgetItem(self.url))
        self.spidermonitor.tblWdg_urls.update()
    
    def spider_closed(self, spider, reason):  
        self.spidermonitor.Btn_break.setEnabled(False)     
        self.spidermonitor.Btn_back.setEnabled(True)