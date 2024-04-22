from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem

from utils.web_scapings.theporndb.api_prepare_for_gui import API_Scene

from utils.helpers.check_biowebsite_status import CheckBioWebsiteStatus
from gui.helpers.set_tootip_text import SetTooltipText, SetDatenInMaske

from gui.helpers.message_show import MsgBox
from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper

class ScrapeThePornDBScene():
    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow
        self.api_link = self.Main.lnEdit_DBThePornDBLink.text()
        api_data = TPDB_Scraper.get_tpdb_data(self.api_link)
        self.get_api_datas_for_scene(api_data)

    #     self.apiThread = ScrapeAPIThePornDBThread(self.api_link) 
    #     self.apiThread.apiFinished.connect(self.apiFinished) 
    #     self.apiThread.start()

    # def apiFinished(self, api_data): 
    #     self.apiThread.quit()
    #     self.apiThread.wait()   
    #     self.get_api_datas_for_scene(api_data)

    def get_api_datas_for_scene(self, api_data):                
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
            self.set_api_scene_infos_ui(api_data)
    
    def set_api_scene_infos_ui(self, api_data):
        quelle = "ThePornDB"
        check_status = CheckBioWebsiteStatus(self.Main)
        check_status.check_loading_labelshow(quelle) 

        theporndb_link = API_Scene.get_scene_data(api_data, 'slug')
        self.Main.addLink(f"https://theporndb.net/scenes/{theporndb_link}")

        synopsis = API_Scene.get_scene_data(api_data, 'description')                
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Synopsis", quelle)                                                    
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, quelle, synopsis) 
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, f"{quelle}: {synopsis}", quelle)

        release_date = API_Scene.get_scene_releasedate(api_data)               
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Release", quelle) 
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, quelle, release_date)
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, f"{quelle}: {release_date}", quelle)

        url = API_Scene.get_scene_data(api_data, ('url'))
        self.set_url_in_table_weblinks(url)

        dauer = API_Scene.get_scene_duration(api_data)              
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Dauer", quelle)
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, quelle, dauer) 
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, f"{quelle}: {dauer}", quelle)

        performers = API_Scene.get_scene_performers(api_data)
        self.set_performers_in_table_performers(performers)

        tags = API_Scene.get_scene_tags(api_data)        
        self.set_tags_in_textEdit(tags)
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Tags", quelle) 
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, f"{quelle}: {tags}", quelle)

        regie = API_Scene.get_scene_data(api_data, 'directors')        
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Regie", quelle) 
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, quelle, regie)
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, f"{quelle}: {regie}", quelle)

        movies = API_Scene.get_scene_data(api_data, 'movies')        
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Movies", quelle) 
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, quelle, movies)
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, f"{quelle}: {movies}", quelle)  

        scene_code = API_Scene.get_scene_data(api_data, 'external_id')        
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("SceneCode", quelle) 
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, quelle, scene_code)
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, f"{quelle}: {scene_code}", quelle) 

        site_name = API_Scene.get_scene_data(api_data, ('site'))
        self.check_site_for_series(site_name.get('name'))
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Serie", quelle) 
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, site_name.get('name'), quelle)    

    ### Wenn der Titel da ist und min. 1 Darsteller da ist, Speicher-Button aktiv ###
        if self.Main.lnEdit_DBTitel.text() and self.Main.tblWdg_files.currentColumn() != -1:
            self.Main.Btn_Speichern.setEnabled(True)        
        check_status.check_loaded_labelshow("ThePornDB")

    def set_url_in_table_weblinks(self, url):
        model = self.Main.lstView_database_weblinks.model()
        urls = [model.data(model.index(row, 0)) for row in range(model.rowCount())]
        if url not in urls:
            self.Main.addLink(url)

    def set_performers_in_table_performers(self, performers):
        for performer in performers:
            for performer_name, alias in performer.items():
                if not (self.Main.tblWdg_DB_performers.findItems(performer_name, Qt.MatchFlag.MatchContains)):
                    self.Main.tblWdg_DB_performers.insertRow(0)
                    self.Main.tblWdg_DB_performers.setItem(0, 0, QTableWidgetItem(performer_name))
                    if alias:
                        self.Main.tblWdg_DB_performers.setItem(0, 1, QTableWidgetItem(alias))

    def set_tags_in_textEdit(self, tags):
        db_tags = self.Main.txtEdit_DBTags.toPlainText().strip(";").split(";")
        thporndb_tags = tags.split(";")
        tags = ";".join(list(set(db_tags + thporndb_tags)))
        self.Main.txtEdit_DBTags.setPlainText(tags)

    def check_site_for_series(self, site_name):
        return None       


        