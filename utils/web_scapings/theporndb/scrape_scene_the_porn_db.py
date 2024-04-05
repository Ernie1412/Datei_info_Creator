from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper

class ScrapeThePornDBScene():
    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow

    def webscrape_scene(self):
        api_url = self.Main.lnEdit_DBThePornDBLink.text()
        api_data = TPDB_Scraper.get_tpdb_data(api_url)

        