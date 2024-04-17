from PyQt6.QtCore import QThread, pyqtSignal

from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper


class ScrapeAPIThePornDBThread(QThread):
    apiFinished = pyqtSignal(dict)
    def __init__(self, api_link, parent: str=None) -> None: 
        super().__init__(parent)
        self.api_link = api_link        
        
    def run(self):        
        api_data = TPDB_Scraper.get_tpdb_data(self.api_link)
        self.apiFinished.emit(api_data)
           