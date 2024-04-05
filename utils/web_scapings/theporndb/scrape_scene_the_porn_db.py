from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper
from gui.helpers.message_show import MsgBox


class ScrapeThePornDBScene():
    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow

    def get_api_datas_for_scene(self):
        api_url = self.Main.lnEdit_DBThePornDBLink.text()
        api_data = TPDB_Scraper.get_tpdb_data(api_url) 
        if api_data.get('message') == 'Unauthenticated.':
            MsgBox(self.Main, "'Unauthenticated' Du bist nicht angemeldet. Bitte melde dich an.","w")
            self.reject() 
            return
        elif api_data.get('message') == 'key missing':
            MsgBox(self.Main, "kein API Key vorhanden. Setze einen in den Einstellungen !","w")
            self.reject()
            return
        elif api_data.get('data') == []:
            MsgBox(self.Main, f"keine Daten gefunden für {self.api_link}!","w")
            self.reject()
            return
        else: 
            self.set_api_infos_ui(api_data)
    
    def set_api_infos_ui(self, api_data):
        uuid, search_count = API_Scene.get_scene_data(api_data, 'id')


        