
from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper
from utils.web_scapings.helpers.helpers import CheckBioWebsiteStatus

class CheckThePornDBLink():
    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow

    def check_scene_api_link(self):
        link = self.Main.lnEdit_DBThePornDBLink.text()
        if not link.startswith('https://api.theporndb.net/scenes/'):
            self.Main.txtEdit_Clipboard.setText(f"{link} ist keine gültige Scene API-URL.")
            self.Main.lnEdit_DBThePornDBLink.setText("")
            self.Main.Btn_Linksuche_in_ThePornDB.setEnabled(False)
            return
        else:
            response = TPDB_Scraper.check_tpdb_data(link)
            if response == 200:
                check_biowebsite_status = CheckBioWebsiteStatus(self.Main)
                check_biowebsite_status.check_OK_labelshow('ThePornDB')
    