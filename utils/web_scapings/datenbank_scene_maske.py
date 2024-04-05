### Grafik Oberfläche ###
from PyQt6.QtCore import QTimer, QCoreApplication
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QTableWidgetItem, QApplication, QTableWidgetSelectionRange, QMessageBox
### internet Kram ###
from playwright.sync_api import sync_playwright, TimeoutError
import requests
from lxml import html

import pyperclip
import re
from datetime import datetime
from typing import Tuple

# import eigene Moduls
from utils.database_settings.database_for_scrapings import ScrapingData
from gui.helpers.set_tootip_text import SetTooltipText, SetDatenInMaske
from utils.database_settings.search_title_from_db import SearchTitle
from utils.database_settings.database_for_settings import Webside_Settings
from utils.web_scapings.scrap_with_requests import VideoUpdater
from utils.helpers.umwandeln import time_format_00_00_00, datum_umwandeln, from_classname_to_import, custom_title
from gui.helpers.message_show import MsgBox

from config import HEADERS

class DatenbankSceneMaske():          
    #### --------------------------------------------------------------------------------------- ####
    def __init__(self, MainWindow):            
        super().__init__() 
        self.Main = MainWindow

    def set_datas_in_database(self):
        set_daten_maske = SetDatenInMaske(self.Main)
        db_websides=ScrapingData(MainWindow=self.Main)        
        id = self.Main.tblWdg_daten.selectedItems()[0].text()
        self.Main.lbl_movie_id.setText(id) 
        ### ----------- setze Studio  ------------ ###
        studio = self.Main.tblWdg_daten.property("studio")
        studio_sides = self.Main.tblWdg_daten.selectedItems()[2].text().split("\n")
        if not studio_sides:            
            studio = Webside_Settings(self.Main).from_link_to_studio(studio_sides[0]) 
        self.Main.set_button_from_studioname(studio)   
        for studio_side in studio_sides:
            self.Main.model_database_weblinks.appendRow(QStandardItem(studio_side))
        ### ----------- Perfomer incl rest in die TableWidget packen ------------ ###
        performs=self.Main.tblWdg_daten.selectedItems()[4].text().split("\n")
        aliass=(self.Main.tblWdg_daten.selectedItems()[5].text()+"\n"*len(performs)).split("\n")
        actions=(self.Main.tblWdg_daten.selectedItems()[6].text()+"\n"*len(aliass)).split("\n")        
        for zeile,(db_performer,alias,action) in enumerate(zip(performs,aliass,actions)):              
            if " <--" in db_performer:
                action=db_performer[db_performer.find(" <--")+4:]
                db_performer=db_performer.replace(" <--"+action,"")
            if " (Credited: " in db_performer:
                alias=db_performer[db_performer.find(" (Credited: ")+12:].replace(")","")
                db_performer=db_performer.replace(" (Credited: "+alias+")","") 
            self.Main.tblWdg_DB_performers.setRowCount(zeile+1)
            self.Main.tblWdg_DB_performers.setItem(zeile,0,QTableWidgetItem(db_performer))
            self.Main.tblWdg_DB_performers.setItem(zeile,1,QTableWidgetItem(alias))
            self.Main.tblWdg_DB_performers.setItem(zeile,2,QTableWidgetItem(action.strip()))  
        ### ----------- Data18 Link in Maske packen ------------ ###          
        data18_link = db_websides.hole_data18link_von_db(id, studio)         
        if data18_link:
            self.Main.lnEdit_DBData18Link.textChanged.disconnect()  # deaktiven 
            set_daten_maske.set_daten_in_maske("lnEdit_DB", "Data18Link", "Datenbank", data18_link) 
            self.Main.lnEdit_DBData18Link.textChanged.connect(self.Main.Web_Data18_change) # aktiven
            self.Main.lbl_checkWeb_Data18URL.setStyleSheet("background-image: url(':/labels/_labels/check.png')")
        ### ----------- ThePornDB in Maske packen ------------ ###         
        tpdb_link = db_websides.hole_theporndblink_von_db(id, studio)         
        if tpdb_link:
            self.Main.lnEdit_DBThePornDBLink.textChanged.disconnect()  # deaktiven 
            set_daten_maske.set_daten_in_maske("lnEdit_DB", "ThePornDBLink", "Datenbank", tpdb_link) 
            self.Main.lnEdit_DBThePornDBLink.textChanged.connect(self.Main.Web_ThePornDB_change) # aktiven
            self.Main.lbl_checkWeb_TPDBURL.setStyleSheet("background-image: url(':/labels/_labels/check.png')")
        ### ----------- IAFD Link in Maske packen ------------ ###
        if self.Main.tblWdg_daten.selectedItems()[3]:
            self.Main.lnEdit_DBIAFDLink.textChanged.disconnect() # deaktiven      
            set_daten_maske.set_daten_in_maske("lnEdit_DB", "IAFDLink", "Datenbank", self.Main.tblWdg_daten.selectedItems()[3].text()) 
            self.Main.lnEdit_DBIAFDLink.textChanged.connect(self.Main.Web_IAFD_change) # aktiven 
            self.Main.lbl_checkWeb_IAFDURL.setStyleSheet("background-image: url(':/labels/_labels/timeout.png')")
        ### ----------- Rest in Maske packen ------------ ###
        self.set_daten_with_tooltip("lnEdit_DB", "Dauer", "Datenbank", self.Main.tblWdg_daten.selectedItems()[7].text())
        self.set_daten_with_tooltip("lnEdit_DB", "Release", "Datenbank", self.Main.tblWdg_daten.selectedItems()[8].text())
        self.set_daten_with_tooltip("lnEdit_DB", "ProDate", "Datenbank", self.Main.tblWdg_daten.selectedItems()[9].text())
        self.set_daten_with_tooltip("lnEdit_DB", "Serie", "Datenbank", self.Main.tblWdg_daten.selectedItems()[10].text())
        self.set_daten_with_tooltip("lnEdit_DB", "Regie", "Datenbank", self.Main.tblWdg_daten.selectedItems()[11].text())
        self.set_daten_with_tooltip("lnEdit_DB", "SceneCode", "Datenbank", self.Main.tblWdg_daten.selectedItems()[12].text())
        self.set_daten_with_tooltip("txtEdit_DB", "Movies", "Datenbank", self.Main.tblWdg_daten.selectedItems()[13].text())
        self.set_daten_with_tooltip("txtEdit_DB", "Synopsis", "Datenbank", self.Main.tblWdg_daten.selectedItems()[14].text())
        self.set_daten_with_tooltip("txtEdit_DB", "Tags", "Datenbank", self.Main.tblWdg_daten.selectedItems()[15].text())  

    def set_daten_with_tooltip(self, widget_typ: str, art: str, quelle: str, daten: str, artist=False) -> None:        
        tooltip_text = f"{quelle}: Kein Eintrag"
        if daten and daten != "No data":            
            tooltip_text = f"{quelle}: {daten[:40]}"
            SetDatenInMaske(self.Main).set_daten_in_maske(widget_typ, art, quelle, daten, artist) 
        SetTooltipText(self.Main).set_tooltip_text(widget_typ, art, tooltip_text, quelle)
   
    def WebSideLink_update(self, studio: str) -> None:        
        tag: str="" 
        response = requests.get(studio, headers=HEADERS)        
        db_webside = ScrapingData(MainWindow=self.Main)
        synopsis, tags = db_webside.hole_movie_infos_from_artist_Tags(studio)
        synopsis_text_element = html.fromstring(response.content).xpath("//div[@class='sc-xz1bz0-0 lgrCSo']/p/text()")
        tags_text_element = html.fromstring(response.content).xpath("//div[@class='sc-xz1bz0-0 lgrCSo']//a/text()")   
        if len(synopsis_text_element)==1:            
            self.txtEdit_DBSynopsis.setText(synopsis_text_element[0].replace('"','\''))           
        if len(tags)>1:
            tags_string = (";".join(tags_text_element)).title().replace("Shaved","Shaved Pussy")
            tag = re.sub(r"\'[A-Z]", lambda match: "'" + match.group(0)[-1].lower(), tags_string)
            self.txtEdit_DBTags.setText(tag)

    def set_arctors_in_table(self):
        self.tblWdg_DB_performers.setRowCount(self.tblWdg_DB_performers.rowCount()+1) 
        self.tblWdg_DB_performers.setItem(self.tblWdg_DB_performers.rowCount()-1,0,QTableWidgetItem(""))
        self.tblWdg_DB_performers.setItem(self.tblWdg_DB_performers.rowCount()-1,1,QTableWidgetItem(""))       
        self.tblWdg_DB_performers.setItem(self.tblWdg_DB_performers.rowCount()-1,2,QTableWidgetItem(""))
        self.tblWdg_DB_performers.setCurrentCell(self.tblWdg_DB_performers.rowCount()-1, 0)

    # Darsteller usw. der Reihe nach in die Datenbank vorbereiten   
    def get_videodata_from_ui(self, performers: str, alias: str, actions: str) -> dict:
        daten_satz = {
            "ID": self.Main.lbl_movie_id.text(),
            "Titel": self.Main.lnEdit_DBTitel.text(),
            "IAFDLink": self.Main.lnEdit_DBIAFDLink.text(),
            "Data18Link": self.Main.lnEdit_DBData18Link.text(),
            "ThePornDB": self.Main.lnEdit_DBThePornDBLink.text(),
            "Performers": performers,
            "Alias": alias,
            "Action": actions,
            "ReleaseDate": self.Main.lnEdit_DBRelease.text(),
            "Dauer": self.Main.lnEdit_DBDauer.text(),
            "SceneCode": self.Main.lnEdit_DBSceneCode.text(),
            "Synopsis": str(self.Main.txtEdit_DBSynopsis.toPlainText()),
            "Tags": str(self.Main.txtEdit_DBTags.toPlainText()),
            "Serie": self.Main.lnEdit_DBSerie.text(),
            "ProDate": self.Main.lnEdit_DBProDate.text(),
            "Regie": self.Main.lnEdit_DBRegie.text(),
            "Movies": str(self.Main.txtEdit_DBMovies.toPlainText()),
        }
        return daten_satz  
    
    def get_performers_from_ui(self) -> Tuple[str, str, str]:
        namen: str = ""
        alias: str = ""
        actions: str = ""
        table = self.Main.tblWdg_DB_performers
        for row in range(self.Main.tblWdg_DB_performers.rowCount()):                        
            namen += f"{table.item(row, 0).text()}\n" if table.item(row, 0) else "\n"
            alias += f"{table.item(row, 1).text()}\n" if table.item(row, 1) else "\n"
            actions += f"{table.item(row, 2).text()}\n" if table.item(row, 2) else "\n"       
        return namen.rstrip("\n"), alias.rstrip("\n"), actions.rstrip("\n")

    # Datensatz updaten 
    def update_db_and_ui(self, studio: str, WebSideLink: str) -> None:
        performers, alias, actions = self.get_performers_from_ui()
        video_data = self.get_videodata_from_ui(performers, alias, actions)
        db_webside = ScrapingData(MainWindow=self.Main)
        if not studio: 
            self.show_error_message("Kein Studio angegeben !") 
            self.clean_label()           
            return
        errorview, neu = db_webside.update_videodaten_in_db(studio, WebSideLink, video_data)        
        if errorview:
            if "Link nicht gefunden in dem" in errorview:
                result = MsgBox(self.Main, f"{errorview} - Soll der Datensatz neu angelegt werden ?","q")
                if result == QMessageBox.StandardButton.Yes:
                    errview , isneu = db_webside.add_neue_videodaten_in_db(studio, WebSideLink, video_data)  
                    if isneu == 1:
                        self.show_success_message(f"{neu} Datensatz wurde in {studio} gespeichert (update)!",f"{neu} Datensatz geaddet")                          
            self.show_error_message(errorview)               
        else:
            if neu:
                self.show_success_message(f"{neu} Datensatz wurde in {studio} gespeichert (update)!",f"{neu} Datensatz aktualisiert")
                scraping_data = ScrapingData(MainWindow=self.Main)
                errorview = scraping_data.hole_link_aus_db(WebSideLink, studio)
                if not errorview:
                    SearchTitle(self.Main).tabelle_erstellen_fuer_movie(studio, WebSideLink)
                else:
                    self.show_error_message(errorview) 
        self.clean_label()

    def show_success_message(self, message_clip, message_status):
        self.Main.txtEdit_Clipboard.setPlainText(message_clip)
        self.Main.lbl_db_status.setStyleSheet("background-color: #01DF3A")
        self.Main.lbl_db_status.setText(message_status)

    def show_error_message(self, message):
        self.Main.txtEdit_Clipboard.setPlainText(message)
        self.Main.txtEdit_Clipboard.setStyleSheet(f'background-color: #FF0000')

    def clean_label(self):
        QTimer.singleShot(500, lambda: self.Main.txtEdit_Clipboard.setStyleSheet('background-color: #FFFDD5'))      
        QTimer.singleShot(2000, lambda: self.Main.txtEdit_Clipboard.setPlainText(""))

    def get_last_page_from_webside(self, baselink: str) -> int:
        last_page_number: int = 2
        db_webside_settings = Webside_Settings(MainWindow=self.Main)
        errview, last_page_xpath, last_page_attri, homepage, start_click, video_page = db_webside_settings.get_last_side_settings(baselink)
        video_updater = VideoUpdater()

        if start_click!="":            
            errorview, content, driver = video_updater.open_url_javascript(baselink + video_page.format(zahl=1), start_click)                                                                                    
        else:
            errorview, content = video_updater.open_url_no_javascript(baselink + video_page.format(zahl=1))
        if errorview:
            MsgBox(self.Main, f"Fehler beim Laden der {baselink} mit dem Fehler: {errorview} / Abbruch !","w")            
            return last_page_number         
        last_page_element = content.xpath(last_page_xpath)
        last_page_text = int(last_page_element[0].get("href")) if last_page_element else 2

        if not last_page_text.isnumeric():
            last_page_number=re.search(video_page.replace("{zahl}", r"(\d+)"), last_page_text).group(1)
        errorview = db_webside_settings.update_letzte_seite(baselink, int(last_page_text))
        if errorview:
            MsgBox(self.Main, f"Fehler {errorview} beim updaten der letzten Seite !","w")      
        return int(last_page_number)  

# Abschluss
if __name__ == '__main__':
    DatenbankSceneMaske()