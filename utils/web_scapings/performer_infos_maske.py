from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView, QLineEdit
from PyQt6.QtCore import Qt,  QCoreApplication
from PyQt6.QtGui import QPixmap, QIcon, QColor, QBrush

import json
from pathlib import Path 
from typing import Tuple
from urllib.parse import urlparse
import time
import logging

from utils.web_scapings.websides import Infos_WebSides
from utils.database_settings.database_for_darsteller import DB_Darsteller
from utils.web_scapings.iafd_performer_link import IAFDInfos
from gui.clearing_widgets import ClearingWidget
from gui.dialog_gender_auswahl import GenderAuswahl
from gui.dialoge_ui.message_show import StatusBar, blink_label, MsgBox

from config import PROJECT_PATH, WEBINFOS_JSON_PATH

class PerformerInfosMaske():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow  
        logging.basicConfig(filename='log_updates.log', level=logging.INFO, 
            format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')      

    def artist_infos_in_maske(self):
        self.Main.set_performer_maske_text_connect(disconnect=True)
        clearing = ClearingWidget(self.Main)
        clearing.clear_maske()
        self.clear_button_color()
        clearing.set_website_bio_enabled(self.Main.get_bio_websites(widget=True), False)
        iafd_infos=IAFDInfos(MainWindow=self.Main)
        infos_webside=Infos_WebSides(MainWindow=self.Main)
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)       
        selected_items = self.Main.tblWdg_performer.selectedItems()
        ### --------- Name Überschrift setzen ------------------------- ###
        self.Main.grpBox_performer.setTitle(f"Performer-Info ID: {selected_items[0].text()}")         
        self.Main.lnEdit_performer_info.setText(selected_items[1].text().strip()) # Name
        self.Main.lnEdit_performer_ordner.setText(selected_items[2].text().strip()) # Ordner
        if self.Main.grpBox_performer.title()!="Performer-Info ID:":
            clearing.set_website_bio_enabled(self.Main.get_bio_websites(widget=True), True)    
        ### --------- Geschlechts QComboBox setzen -------------------- ###         
        gender_auswahl = GenderAuswahl(self.Main, False)
        gender_auswahl.set_icon_in_gender_button(selected_items[5].text())        
        ### --------- Rasse QComboBox setzen ------------------------- ### 
        self.set_rasse_in_combobox(selected_items[0].text(), infos_webside)        
        ### --------- Nation QComboBox setzen -- von englisch(DB) in deutsch(Maske) ------ ###        
        self.set_nations_in_labels(selected_items[7].text(), infos_webside)  
        ### --------- Fan Side/OnlyFans QComboBox setzen -------------- ###
        self.Main.set_social_media_in_buttons(selected_items[10].text())
        ### --------- Quell Links in QTableWidget setzen -------------- ### 
        self.update_names_linksatz_in_ui(selected_items[0].text())  
        ### --------- IAFD Link setzen -------------------------------- ### 
        if selected_items[3].text():            
            if selected_items[3].text()=="N/A":
                self.Main.chkBox_iafd_enabled.setChecked(False) # IAFD feld deaktivieren                              
                self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(False)
            else:
                self.Main.chkBox_iafd_enabled.setChecked(True)
                self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)
                self.Main.lbl_checkWeb_IAFD_artistURL.setStyleSheet("background-image: url(':/labels/_labels/check.png')")
            infos_webside.set_daten_in_maske("lnEdit_DB", "IAFD_artistLink", "Datenbank", selected_items[3].text(), artist=True)
        elif self.Main.chkBox_get_autom_iafd.isChecked():
             self.Main.lnEdit_create_iafd_link.setText(selected_items[1].text())                      
             iafd_infos.get_IAFD_performer_link() 
             self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)         
        ### --------- Bio Website(u.a. BabePedia) Link setzen -------------------------------- ###
        if selected_items[4].text():
            for bio_sites in selected_items[4].text().split("\n"):                      
                self.set_bio_websites_tooltip(bio_sites)  
        ### ----------- Rest in Maske packen ------------ ###        
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "birthday", "Datenbank", selected_items[8].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "birthplace", "Datenbank", selected_items[9].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "boobs", "Datenbank", selected_items[11].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "weight", "Datenbank", selected_items[12].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "height", "Datenbank", selected_items[13].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "body", "Datenbank", selected_items[14].text(),artist=True)
        infos_webside.set_daten_with_tooltip("txtEdit_performer_", "piercing", "Datenbank", selected_items[15].text(),artist=True)
        infos_webside.set_daten_with_tooltip("txtEdit_performer_", "tattoo", "Datenbank", selected_items[16].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "hair", "Datenbank", selected_items[17].text(), artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "eye", "Datenbank", selected_items[18].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "activ", "Datenbank", selected_items[19].text(),artist=True)        
        ### ----------- IAFD Image in Label setzen ------- ###
        errview, image_pfad = datenbank_darsteller.get_iafd_image(selected_items[0].text())
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            infos_webside.set_tooltip_text("lbl_", "iafd_image", f"Datenbank: '{image_pfad}'", "Datenbank")
            pixmap = QPixmap()
            pixmap.load(str(image_pfad))
            self.Main.stacked_webdb_images.setCurrentWidget(self.Main.stacked_iafd_label)
        else:
            infos_webside.set_tooltip_text("lbl_", "iafd_image", f"Datenbank: 'Kein Bild gespeichert'", "Datenbank")                              
            pixmap = QPixmap(":/labels/_labels/kein-bild.jpg")                   
        self.Main.lbl_iafd_image.setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))        
        ### ----------- BabePedia Image in Label setzen ------- ###
        errview, image_pfad = datenbank_darsteller.get_babepedia_image(selected_items[0].text())
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            infos_webside.set_tooltip_text("lbl_", "babepedia_image", f"Datenbank: '{image_pfad}'", "Datenbank")
            pixmap = QPixmap()
            pixmap.load(str(image_pfad))
            self.Main.stacked_webdb_images.setCurrentWidget(self.Main.stacked_babepedia_label)
        else:
            infos_webside.set_tooltip_text("lbl_", "babepedia_image", f"Datenbank: 'Kein Bild gespeichert'", "Datenbank")                              
            pixmap = QPixmap(":/labels/_labels/kein-bild.jpg")                   
        self.Main.lbl_babepedia_image.setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))
        self.Main.set_performer_maske_text_connect(disconnect=False)         

    def set_bio_websites_tooltip(self, bio_sites: str):                
        for bio_url_key, bio_url_value in self.Main.get_bio_websites().items(): # widget : url
            if bio_sites.startswith(bio_url_value):
                getattr(self.Main,f"Btn_performer_in_{bio_url_key}").setToolTip(bio_sites)

    def set_rasse_in_combobox(self, artist_id, infos_webside):        
        database_darsteller = DB_Darsteller(self.Main)
        rassen_ids = database_darsteller.get_rassenids_from_artistid(int(artist_id))
        for rassen_id in rassen_ids:
            self.Main.cBox_performer_rasse.setChecked(rassen_id-1)         
        rasse=self.Main.cBox_performer_rasse.currentText()  
        infos_webside.set_tooltip_text("cBox_performer_", "rasse", f"Datenbank: {rasse}", "Datenbank")

    def set_nations_in_labels(self, nations: str, infos_webside, art="Datenbank"):
        nations=nations.split(", ") if nations else ""
        datenbank_darsteller = DB_Darsteller(self.Main)
        for zahl, nation_ger in enumerate(nations):
            nation_shortsymbol=datenbank_darsteller.get_shortsymbol_from_german(nation_ger)
            if nation_shortsymbol==None:
                print(f"Nation '{nation_ger}' nicht in Datenbank gefunden")
            else:
                getattr(self.Main,f"lbl_performer_nation_{zahl}").setProperty("nation", nation_ger)            
                getattr(self.Main,f"lbl_performer_nation_{zahl}").setStyleSheet(f"background-image: url(:/labels/_labels/nations/{nation_shortsymbol.lower()}.png);")
                infos_webside.set_tooltip_text(f"lbl_performer_nation_{zahl}", "", f"{art}: {nation_ger}", art)

    def get_social_media_from_buttons(self) -> str: 
        social_medias: str=""
        for index in range(10):
            social_media=getattr(self.Main, f"Btn_performers_socialmedia_{index}").toolTip().replace("Datenbank: ", "")
            if social_media:
                social_medias += social_media +"\n"
        return social_medias[:-1]
    
    def get_bio_websites_from_buttons(self) -> str:
        bio_websites: str=""
        for key in self.Main.get_bio_websites(widget=True):
            bio_website=getattr(self.Main, f"Btn_performer_in_{key}").toolTip()
            if bio_website:
                bio_websites += bio_website +"\n"
        return bio_websites[:-1]

    def get_artistdata_from_ui(self, database: bool=False) -> Tuple[dict, list]:
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
        artist_id = int(self.Main.grpBox_performer.title().replace("Performer-Info ID: ",""))
        ### -------------- Geschlecht für update vorbereiten ------------------ ###        
        gender_auswahl = GenderAuswahl(self.Main, False)
        gender = gender_auswahl.get_gender_from_button()        
        ### -------------- RassenID für update vorbereiten -------------------- ### 
        rassen = "/".join(self.Main.cBox_performer_rasse.get_checked_items())        
        ### -------------- Nation für update vorbereiten ----------------------- ###         
        nations = self.get_nations_from_labels()         
        ### -------------------------------------------------------------------- ###
        daten_satz = {
            "ArtistID" : artist_id,
            "Name": self.Main.lnEdit_performer_info.text().strip(),
            "Ordner": self.Main.lnEdit_performer_ordner.text().strip(),
            "IAFDLink": self.Main.lnEdit_DBIAFD_artistLink.text().strip(),
            "BabePedia": self.get_bio_websites_from_buttons(),
            "Geschlecht": gender,            
            "Rassen": rassen,
            "Nation": nations,            
            "Geburtstag": self.Main.lnEdit_performer_birthday.text().strip(),
            "Birth_Place": self.Main.lnEdit_performer_birthplace.text().strip(),
            "OnlyFans": self.get_social_media_from_buttons(),
            "Boobs": self.Main.lnEdit_performer_boobs.text().strip(),
            "Gewicht": int(self.Main.lnEdit_performer_weight.text() or 0),
            "Groesse": int(self.Main.lnEdit_performer_height.text() or 0),
            "Bodytyp": self.Main.lnEdit_performer_body.text().strip(),
            "Piercing": self.Main.txtEdit_performer_piercing.toPlainText().strip(),
            "Tattoo": self.Main.txtEdit_performer_tattoo.toPlainText().strip(),
            "Haarfarbe": self.Main.lnEdit_performer_hair.text().strip(),
            "Augenfarbe": self.Main.lnEdit_performer_eye.text().strip(),
            "Aktiv": self.Main.lnEdit_performer_activ.text().strip(),     }
        names_link_satz = []
        if database:            
            names_link_satz=self.nameslink_datensatz_in_dict(names_link_satz)
        return daten_satz, names_link_satz
    
    def get_nations_from_labels(self) -> str:
        nations: str = []
        for zahl in range(7): 
            nation=getattr(self.Main,f"lbl_performer_nation_{zahl}").property("nation") 
            if nation:
                nations.append(nation)
        return ", ".join(nations)
    
    def update_nations(awlf, nations_ger: str, artist_id: int, datenbank_darsteller) -> str:
        nation_message=""
        nations_ids: list = []
        for nation_german in nations_ger.split(", "):
            id = datenbank_darsteller.get_nations_id_from_nations_ger(nation_german)
            if id >-1:                
                nations_ids.append(id)
        errview, is_addet = datenbank_darsteller.update_or_add_nation_datensatz(nations_ids, artist_id)
        if errview and not "Nation: None nicht in der Datenbank !":
            nation_message=f".❌Fehler beim Nation Adden: {errview}" 
        elif is_addet:
            nation_message=".➕Eine Nation wurde geaddet/updated/gelöscht"
        return nation_message
    
    def update_rassen(self, rassen_ger: str, artist_id: int, datenbank_darsteller) -> str:
        rassen_message: str = ""
        rassen_ids: list = []
        for rasse_german in rassen_ger.split("/"):
            id = datenbank_darsteller.get_rassen_id_from_rassen_ger(rasse_german)
            if id >-1: 
                rassen_ids.append(id)
        errview, is_addet = datenbank_darsteller.update_or_add_rassen_datensatz(rassen_ids, artist_id)
        if errview and not "Rasse: None nicht in der Datenbank !":
            rassen_message=f".❌Fehler beim Rasse Adden: {errview}" 
        elif is_addet:
            rassen_message=".➕Eine Rasse wurde geaddet/updated/gelöscht"
        return rassen_message
    
    def nameslink_datensatz_in_dict(self, names_link_satz):
        for zeile in range(self.Main.tblWdg_performer_links.rowCount()):
            pfad = self.file_rename_and_move(zeile)
            link = self.Main.tblWdg_performer_links.item(zeile, 1).text()
            alias = self.Main.tblWdg_performer_links.item(zeile, 3).text()
            a=self.Main.lnEdit_IAFD_artistAlias.text()
            alias = self.Main.lnEdit_IAFD_artistAlias.text() if link.startswith("https://www.iafd.com/person.rme/perfid=") else alias   
            names_id_str = self.Main.tblWdg_performer_links.item(zeile, 0).text()            
            row_data = {
                "NamesID": int(names_id_str) if names_id_str is not None and names_id_str.isdigit() else -1,
                "Link": link,
                "Image": pfad,
                "Alias": alias  }
            names_link_satz.append(row_data)
        return names_link_satz

    def file_rename_and_move(self, zeile: int) -> str:
        old_path=self.Main.tblWdg_performer_links.item(zeile, 2).text()
        folder = self.Main.lnEdit_performer_ordner.text()
        if old_path and Path(old_path).parents[1]:
            old_folder=Path(old_path).parent.name
            pic_folder=Path(old_path).parents[1]                    
            new_path = Path(pic_folder, folder, Path(old_path).name)
            if new_path!=Path(old_path):
                if not Path(PROJECT_PATH, pic_folder, folder).exists(): # makedir, wenn keins da
                    Path(PROJECT_PATH, pic_folder, folder).mkdir()
                old_path_project = Path(PROJECT_PATH, old_path)
                new_path_project = Path(PROJECT_PATH, new_path)
                try:
                    old_path_project.rename(new_path_project) # verschiebt und renamed zugleich
                except FileNotFoundError as e:
                    StatusBar(self.Main, f"Error bei: {old_path} mit {e}", "#ff0000")
                else:
                    if old_path_project.is_dir() and not any(old_path_project.iterdir()): # altes Verzeichnis löschen, wenn es leer ist                    
                        old_path_project.rmdir()
                    old_path=str(new_path).replace("\\","/") # für die Tabelle
        return old_path   

    def set_icon_in_tablewidget(self, zeile, image):
        item = QTableWidgetItem() 
        if image and Path(PROJECT_PATH / image).exists():                
            item.setIcon(QIcon(':/labels/_labels/check.png'))  
        else:
            item.setIcon(QIcon(':/labels/_labels/error.png'))
        self.Main.tblWdg_performer_links.setItem(zeile,4,item)
    
    def put_daten_satz_in_tablewidget(self): 
        daten_satz,_ = self.get_artistdata_from_ui()
        artist_id=daten_satz["ArtistID"]
        for zeile in range(self.Main.tblWdg_performer.rowCount()):
            item = self.Main.tblWdg_performer.item(zeile, 0)
            if item is not None and str(artist_id) in item.text():                
                for spalte, (key, value) in enumerate(daten_satz.items()):
                    self.Main.tblWdg_performer.setItem(zeile, spalte, QTableWidgetItem(str(value)))
                    self.Main.tblWdg_performer.update()
                    self.Main.tblWdg_performer.selectRow(zeile)
                return artist_id, zeile+1  
        return 0, 0        

    def update_datensatz(self):
        self.Main.Btn_DBArtist_Update.setEnabled(False)         
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)        
        nameslink_msg: str=""
        #### --------------- IAFD Image und andere Images werden gespeichert ----------------------------- ####
        iafd_message = self.save_iafd_image_in_datenbank()                
        #### -------------------------------------------------------------- ####     
        artist_id, zeile= self.put_daten_satz_in_tablewidget()
        rassen = "/".join(self.Main.cBox_performer_rasse.get_checked_items())
        rassen_message = self.update_rassen(rassen, artist_id, datenbank_darsteller)
        ### -------------- Nation für update vorbereiten ----------------------- ###         
        nations = self.get_nations_from_labels()
        nation_message = self.update_nations(nations, artist_id, datenbank_darsteller)
        daten_satz_ui, names_link_satz_ui=self.get_artistdata_from_ui(database=True)                 
        artist_id = daten_satz_ui["ArtistID"]
        self.update_names_linksatz_in_ui(artist_id)
        ### ------------ Update was in der Tabelle von Performer_Links drin ist --------------- ###
        is_neu_linksatz, is_update_linksatz = self.update_and_check_names_linksatz_for_db(names_link_satz_ui, artist_id, datenbank_darsteller)
        ### --------------- Anzeige was alles neu, updated ist und refresh tabelle -------------------- ###         
        if (is_neu_linksatz or is_update_linksatz) > 0:
            self.update_names_linksatz_in_ui(daten_satz_ui["ArtistID"])
            nameslink_msg = "🔗NamesLink" 
        ### ------------ Check auf Veränderungen in der datenbank Maske ------------ ###
        errview, is_update_datensatz = self.update_and_check_datensatz_for_db(daten_satz_ui, artist_id, datenbank_darsteller)        
        ### ------------ Update alles was oben in der Maske drin ist --------------- ###         
        datensatz_msg: str=""
        if errview:
            datensatz_msg=f"❌Fehler: {errview}"
            blink_label(self.Main, "lbl_db_status", "#FF0000")
        else:
            self.clear_button_color()
            if is_update_datensatz: # check Maske wurde updated 
                datensatz_msg = " 🙍‍♂️Datensatz und" if nameslink_msg else " 🙍‍♂️Datensatz"
                blink_label(self.Main, "lbl_db_status", "#74DF00") 
        message= f"Update {artist_id}: {datensatz_msg}{nameslink_msg}{rassen_message}{iafd_message}"
        self.Main.txtBrowser_loginfos.append(message)
        self.Main.txtBrowser_loginfos.verticalScrollBar().setSliderPosition(self.Main.txtBrowser_loginfos.verticalScrollBar().maximum()) 
        logging.info(message)
        self.Main.lbl_db_status.setText(message+nation_message)

    def clear_button_color(self):
        clearing_widget = ClearingWidget(self.Main)
        clearing_widget.invisible_performer_btn_anzahl()
        widgets = clearing_widget.performers_tab_widgets("lineprefix_perf_textprefix_perf_lineiafd")
        for widget in widgets: # masken farbe wieder bereinigen bei erfolgreichen update
            self.Main.set_color_stylesheet(widget, color_hex='#FFFDD5')

    def update_and_check_names_linksatz_for_db(self, names_link_satz_ui, artist_id, datenbank_darsteller):
        is_neu_datensatz: int=0 
        is_update_datensatz: int=0
        
        for linksatz in names_link_satz_ui:
            url=linksatz["Link"]
            studio_link = f"{urlparse(url).scheme}://{urlparse(url).netloc}/"                       
            studio_id = datenbank_darsteller.get_studio_id_from_baselink(studio_link)
            if studio_id > -1:                                
                linksatz_list_db = datenbank_darsteller.get_nameslink_dataset_from_namesid(linksatz["NamesID"])
                linksatz_list_ui = list(linksatz.values())
                if linksatz_list_db and linksatz_list_ui != linksatz_list_db:                    
                    is_update_datensatz += datenbank_darsteller.update_performer_names_link(artist_id, linksatz, studio_id)
                elif not linksatz_list_db:
                    is_neu_datensatz_db, _ = datenbank_darsteller.add_db_artistlink(artist_id, linksatz, studio_id)  
                    is_neu_datensatz += is_neu_datensatz_db
            else:
                StatusBar(self.Main, f"keine Studio ID für {studio_link} gefunden, kein update, add möglich !","#FF0000")
        return is_neu_datensatz, is_update_datensatz
    
    def update_and_check_datensatz_for_db(self, datensatz_ui, artist_id, datenbank_darsteller):
        is_update_datensatz: int=0
        errview: str=None
        datensatz_db = datenbank_darsteller.get_performer_dataset_from_artistid(artist_id)
        if datensatz_db[0]:
            if any(datensatz_db[0][key] != datensatz_ui[key] for key in datensatz_db[0]):
                errview, is_update_datensatz= datenbank_darsteller.update_performer_datensatz(datensatz_ui)            
        return errview, is_update_datensatz
    
    def translate_rassen_ger_in_number(self, rassen, datenbank_darsteller) -> list:
        rassen_ids: list=[]
        for rasse in rassen.split("/"):
            if datenbank_darsteller.get_rassen_id_from_rassen_ger(rasse)!= -1:
                rassen_ids.append(datenbank_darsteller.get_rassen_id_from_rassen_ger(rasse))
        return rassen_ids

    def update_tabelle(self):
        iafd: int=0
        bio_infos: int=0        
        current_iafd: int=1
        now_iafd: int=1
        now_bio: int=1
        table_performer_count = self.Main.tblWdg_performer.rowCount()
        self.Main.stacked_image_infos.setCurrentWidget(self.Main.logger_infos)

        for zeile in range(table_performer_count):
            if self.Main.tblWdg_performer.item(zeile,3).text().startswith("https://www.iafd.com/person.rme/perfid="):
                iafd+=1
            if self.Main.tblWdg_performer.item(zeile,3).text() == "N/A":
                bio_infos+=1             
        no_infos = table_performer_count-iafd-bio_infos        
        self.Main.chkBox_get_autom_iafd.setChecked(True)

        for zeile in range(table_performer_count):            
            self.setinfo_label(now_iafd, iafd,now_bio,bio_infos,current_iafd,no_infos, table_performer_count)
            item=self.Main.tblWdg_performer.item(zeile, 0)
            item.setSelected(True)
            self.Main.tblWdg_performer.selectRow(zeile)            
            self.Main.tblWdg_performer.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
            
            if self.Main.tblWdg_performer.selectedItems()[3].text().startswith("https://www.iafd.com/person.rme/perfid="):
                now_iafd+=1
                continue
            elif self.Main.tblWdg_performer.selectedItems()[3].text() == "N/A":
                now_bio+=1
                continue
            
            current_iafd+=1
            QCoreApplication.processEvents()
            self.artist_infos_in_maske()

            iafd_infos = IAFDInfos(MainWindow=self.Main)
            iafd_url=self.Main.lnEdit_DBIAFD_artistLink.text()
            artist_id = self.Main.grpBox_performer.title().replace("Performer-Info ID: ","")
            name = self.Main.lnEdit_performer_info.text()

            iafd_infos.load_IAFD_performer_link(iafd_url, artist_id, name) # scrape IAFD infos
            if Path(WEBINFOS_JSON_PATH).exists() and json.loads(WEBINFOS_JSON_PATH.read_bytes()):           
                self.set_iafd_infos_in_ui() # setzt die scraped infos in die DB Maske
                self.update_datensatz() # und speichert alles in die Datenbank
        MsgBox(self.Main,"Fertig !","i")

    def setinfo_label(self,now_iafd, iafd,now_bio,bio_infos,current_iafd,no_infos, table_performer_count):
        self.Main.lbl_infos_on_imagestacked.setText(f"IAFD: {now_iafd}|{iafd} / kein IAFDLink: {now_bio}|{bio_infos} / durchsuche: {current_iafd}|{no_infos} gesamt: {table_performer_count}")   
    
    ### ------------------- speichert Link, Image, Alias in die Datenbank ------------------ ###
    def save_iafd_image_in_datenbank(self, artist_id: int=-1, ordner=None) -> str: # default ID von der datenbank Maske nehmen
        iafd_message: str=""
        image_pfad: str=None
        iafd_link = self.Main.lnEdit_DBIAFD_artistLink.text()
        if iafd_link == "N/A":
            return ".🚫kein IAFD Daten vorhanden !"
        
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
        if artist_id == -1:
            artist_id = self.get_artist_id_from_groupbox(self.Main.grpBox_performer.title())                    
            _,image_pfad = datenbank_darsteller.get_iafd_image(artist_id)

        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            return ".🖼️IAFD Bild ist schon ✅vorhanden"

        pixmap = self.Main.lbl_iafd_image.pixmap()
        if not pixmap:
            return ".🖼️IAFD Bild nicht im Label,🚫kein speichern möglich"        
        
        if not iafd_link:
            return ".🖼️IAFD Link 🚫nicht vorhanden !"

        perfid = self.get_perfid_from_iafd_link(iafd_link)
        if not perfid:
            return ".⚠️Es ist kein IAFD Link  !" 

        if Path(f"__artists_Images/{ordner}/[IAFD]-{perfid}.jpg").exists():
            artist_id=datenbank_darsteller.get_artistid_from_nameslink(f"__artists_Images/{ordner}/[IAFD]-{perfid}.jpg")     
            
        if ordner == None:
            ordner = self.Main.lnEdit_performer_ordner.text()        
        errview, is_added = self.names_link_from_iafd(ordner, perfid, iafd_link, artist_id, datenbank_darsteller)                     
        if is_added: # IAFD Bild muss verschoben werden
            iafd_message = ",🖼️IAFD Bild wurde gespeichert✔️"                                    
        else:
            iafd_message = f",🖼️IAFD Bild wurde nicht gespeichert❌(Error: {errview})"
        return iafd_message
    
    def names_link_from_iafd(self, ordner, perfid, iafd_link, artist_id, datenbank_darsteller):
        if not Path(WEBINFOS_JSON_PATH).exists(): # get iafd_infos from ui
            iafd_infos = {"alias": self.Main.lnEdit_IAFD_artistAlias.text(),
                          "image_pfad": f"__artists_Images/{ordner}/[IAFD]-{perfid}.jpg"}
        else:
            infos = json.loads(WEBINFOS_JSON_PATH.read_bytes())
            iafd_infos = infos.get("iafd","")
        alias = iafd_infos.get("alias","")
        
        new_image_pfad=f"__artists_Images/{ordner}/[IAFD]-{perfid}.jpg"
        old_image_pfad = iafd_infos.get("image_pfad","")

        if old_image_pfad:
            iafd_infos["image_pfad"]=str(Path(PROJECT_PATH, new_image_pfad))
            if not Path(Path(PROJECT_PATH / new_image_pfad).parent).exists():
                Path(Path(PROJECT_PATH / new_image_pfad).parent).mkdir()
            if Path(old_image_pfad).exists() and old_image_pfad != new_image_pfad:
                Path(old_image_pfad).rename(Path(PROJECT_PATH, new_image_pfad))
            else:
                new_image_pfad=None
                iafd_infos["image_pfad"]=None        
            infos["iafd"]=iafd_infos
            json.dump(infos,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True)
        names_link_iafd = {"Link": iafd_link,
                            "Image": new_image_pfad,
                            "ArtistID": artist_id,
                            "Alias": alias     }  
        self.update_names_linksatz_in_ui(names_link_iafd) 
        return datenbank_darsteller.add_performer_link_and_image(names_link_iafd)
    
    def update_iafd_datensatz_from_json(self, artist_id: int, ordner: str) -> str:
        infos = json.loads(WEBINFOS_JSON_PATH.read_bytes())
        iafd_infos = infos.get("iafd","")
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
        old_datensatz = datenbank_darsteller.get_performer_dataset_from_artistid(artist_id)
        old_datensatz = old_datensatz[0]
        daten_satz = {
            "ArtistID" : artist_id,            
            "Ordner": ordner,
            "IAFDLink": iafd_infos.get("IAFDLink"),            
            "Geschlecht": old_datensatz.get("Geschlecht") or iafd_infos.get("Geschlecht") or 1,           
            "Rassen": old_datensatz.get("Rassen") or iafd_infos.get("Rassen"),
            "Nation": old_datensatz.get("Nation") or iafd_infos.get("Nation"),            
            "Geburtstag": old_datensatz.get("Geburtstag") or iafd_infos.get("Geburtstag"),
            "Birth_Place": old_datensatz.get("Birth_Place") or iafd_infos.get("Birth_Place"),
            "OnlyFans": old_datensatz.get("OnlyFans") or iafd_infos.get("OnlyFans"),
            "Boobs": old_datensatz.get("Boobs") or iafd_infos.get("Boobs"),
            "Gewicht": old_datensatz.get("Gewicht") or iafd_infos.get("Gewicht"),
            "Groesse": old_datensatz.get("Groesse") or iafd_infos.get("Groesse"),            
            "Piercing": old_datensatz.get("Piercing") or iafd_infos.get("Piercing"),
            "Tattoo": old_datensatz.get("Tattoo") or iafd_infos.get("Tattoo"),
            "Haarfarbe": old_datensatz.get("Haarfarbe") or iafd_infos.get("Haarfarbe"),            
            "Aktiv": old_datensatz.get("Aktiv") or iafd_infos.get("Aktiv"),                                       
                    }
        errview, is_update= datenbank_darsteller.update_performer_datensatz(daten_satz)
        if is_update:
            return "🖼️IAFD Datensatz wurde gespeichert✔️"
        else:
            return f"🖼️IAFD Datensatz wurde nicht gespeichert❌(Error: {errview})"

        
    ### ---------------- Hilfs Funktionen für 'save_iafd_image_in_datenbank' ------------------------- ###    
    def get_artist_id_from_groupbox(self, title):
        return int(title.replace("Performer-Info ID: ", ""))
    
    def save_image_to_disk(self, image_path, pixmap):
        if not Path(image_path.parent).exists():
            Path(image_path.parent).mkdir(parents=True)
        pixmap.save(str(image_path), "JPEG")

    def get_perfid_from_iafd_link(self, iafd_link):
        try:
            return iafd_link.replace("https://www.iafd.com/person.rme/perfid=", "").split("/", 1)[0]
        except ValueError:
            return None
    #### ----------------------------------------------------------------------------- ####
        
    def is_ein_bild_dummy_im_label(self):
        kein_bild_vorhanden_image_path = ":/labels/_labels/kein-bild.jpg" 
        kein_bild_vorhanden_image = QPixmap(str(kein_bild_vorhanden_image_path)).toImage()        
        # Lade das aktuelle Bild im Label
        current_image = self.Main.lbl_iafd_image.pixmap().toImage() if self.Main.lbl_iafd_image.pixmap() else None 
        return current_image == kein_bild_vorhanden_image # Überprüfe, ob die Bilder gleich sind

    ### ---------------------------------IAFD Infos ------------------------------------------ ### 
    def set_iafd_infos_in_ui(self):
        if not Path(WEBINFOS_JSON_PATH).exists():
            MsgBox(self.Main, "Keine IAFD Daten vorhanden !","w")
            return
        ### --------------- Ausgabe in UI Maske ------------------------ ###        
        infos = json.loads(WEBINFOS_JSON_PATH.read_bytes())
        iafd_infos = infos["iafd"]
        if not iafd_infos:
            MsgBox(self.Main, "Keine IAFD Daten vorhanden !","w")
            return
        datensatz_darsteller = DB_Darsteller(self.Main)
        # --------- gender ----------- #
        sex=iafd_infos.get("Geschlecht")
        if sex:                
            GenderAuswahl(self.Main, False).set_icon_in_gender_button(sex) 
        # --------- Rasse ----------- #
        rassen=iafd_infos.get("Rassen")
        if rassen:             
            for rasse_ger in rassen.split("/"):
                rasse_id = datensatz_darsteller.get_rassen_id_from_rassen_ger(rasse_ger)                          
                if rasse_id != -1:
                    #self.Main.Btn_DBArtist_Update.setEnabled(True)
                    self.Main.cBox_performer_rasse.setChecked(int(rasse_id)-1) 
        # --------- IAFD Namen/Alias ----------- #
        alias=iafd_infos.get("alias")
        if alias:
            self.Main.lnEdit_IAFD_artistAlias.setText(alias) 
            self.Main.performer_text_change("lnEdit_IAFD_artistAlias", color_hex='#FFFD00') 
        # --------- Nationen ------------------- #
        nations_ger=iafd_infos.get("deutsch_nations")        
        if nations_ger:
            i=1
            while getattr(self.Main,f"lbl_performer_nation_{i}").property("nation"):
                ClearingWidget(self.Main).clear_nations(i)
                i+=1
            infos_webside=Infos_WebSides(MainWindow=self.Main)
            self.set_nations_in_labels(nations_ger, infos_webside, "IAFD")
        # --------- Haarfarbe ------------------- #
        hair_color=iafd_infos.get("Haarfarbe")
        if hair_color:            
            self.check_selections_count("hair","1", hair_color)            
        # --------- Gewicht ------------------- #
        gewicht=iafd_infos.get("Gewicht")
        if gewicht:            
            self.check_selections_count("weight","1", f"{gewicht}")
        # --------- Körper-Größe ------------------- #
        groesse=iafd_infos.get("Groesse")
        if groesse:           
            self.check_selections_count("height","1", f"{groesse}")
        # --------- Geburts-Ort ------------------- #
        geburtsort=iafd_infos.get("Birth_Place")
        if geburtsort:            
            self.check_selections_count("birthplace","1", geburtsort)
        # --------- Geburts-Tag ------------------- #
        geburtstag=iafd_infos.get("Geburtstag")
        if geburtstag:
            self.check_selections_count("birthday","1", geburtstag)
        # --------- Geburts-Tag ------------------- #
        piercing=iafd_infos.get("Piercing")
        if piercing:
            self.check_selections_count("piercing","1", piercing)
        # --------- Geburts-Tag ------------------- #
        tattoo=iafd_infos.get("Tattoo")
        if tattoo:
            self.check_selections_count("tattoo","1", tattoo)
        # --------- Geburts-Tag ------------------- #
        aktiv=iafd_infos.get("Aktiv")
        if aktiv:
            self.check_selections_count("activ","1", aktiv) 
        # --------- boobs ------------------- #
        boobs=iafd_infos.get("Boobs")
        if boobs:            
            self.check_selections_count("boobs","1", boobs)
        # --------- IAFD Image ---------------- #
        id = self.Main.grpBox_performer.title().replace("Performer-Info ID: ","") # ArtistID
        name = self.Main.lnEdit_performer_info.text() # Performer 'Name'        
        image_pfad=iafd_infos.get("image_pfad")        
        if image_pfad:
            self.Main.stacked_webdb_images.setCurrentWidget(self.Main.stacked_iafd_label)                  
            self.load_and_scale_pixmap(image_pfad, self.Main.lbl_iafd_image)  

    def check_selections_count(self, type, count, value):                        
        button = getattr(self.Main,f"Btn_{type}_selection")
        label = getattr(self.Main, f"txtEdit_performer_{type}") if type in ["piercing", "tattoo"] else getattr(self.Main, f"lnEdit_performer_{type}")
        current_text = label.text() if isinstance(label, QLineEdit) else label.toPlainText()
        if current_text != value:
            label.setText(value)
            button.setVisible(True)
            button.setText("1")            

    def load_and_scale_pixmap(self, image_path, label):
        pixmap = QPixmap()        
        pixmap.load(str(image_path))                
        label_height = 280
        try:
            label_width = int(label_height * pixmap.width() / pixmap.height())
        except ZeroDivisionError as e:
            print(f"load_and_scale_pixmap -> {self.Main.lnEdit_performer_info.text()} -> Fehler: {e}")
            return
        label.setPixmap(pixmap.scaled(label_width, label_height, Qt.AspectRatioMode.KeepAspectRatio))
        QCoreApplication.processEvents() 

    ### ------------------------------------------------------------------------------------------------- ###    
    def update_names_linksatz_in_ui(self, artist_id: int):
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        nameslink_datensatz = datenbank_darsteller.get_quell_links(artist_id) #ArtistID -> DB_NamesLink.NamesID
        for zeile, (id, link, image, alias) in enumerate(zip(*nameslink_datensatz)):                   
            self.Main.tblWdg_performer_links.setRowCount(zeile+1)
            self.Main.tblWdg_performer_links.setItem(zeile,0,QTableWidgetItem(f"{id}"))            
            self.Main.tblWdg_performer_links.setItem(zeile,1,QTableWidgetItem(link))
            self.Main.tblWdg_performer_links.setItem(zeile,2,QTableWidgetItem(image))
            self.Main.tblWdg_performer_links.setItem(zeile,3,QTableWidgetItem(alias))
            self.set_icon_in_tablewidget(zeile, image)
            self.setColortoRow(self.Main.tblWdg_performer_links,zeile,'#FFFDD5')
            if link.startswith("https://www.iafd.com/person.rme/perfid="):
                self.Main.lnEdit_IAFD_artistAlias.setText(alias)                                           
        self.Main.tblWdg_performer_links.update()
        self.Main.tblWdg_performer_links.resizeColumnsToContents()        

    def setColortoRow(self, table, rowIndex, color_hex):
        if color_hex=='#FFFD00':
            self.Main.Btn_DBArtist_Update.setEnabled(True)
        else:
            self.Main.Btn_DBArtist_Update.setEnabled(False)
        color = QColor(color_hex)
        brush = QBrush(color)
        for column in range(table.columnCount()-1):
            table.item(rowIndex, column).setBackground(color)

# Abschluss
if __name__ == '__main__':
    PerformerInfosMaske()