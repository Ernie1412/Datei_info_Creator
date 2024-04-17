from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView, QLineEdit
from PyQt6.QtCore import Qt,  QCoreApplication
from PyQt6.QtGui import QPixmap, QIcon, QColor, QBrush

import json
from pathlib import Path 
from typing import Tuple
from urllib.parse import urlparse
import time
import logging

from utils.web_scapings.datenbank_scene_maske import DatenbankSceneMaske
from gui.helpers.set_tootip_text import SetDatenInMaske, SetTooltipText
from utils.database_settings.database_for_darsteller import DB_Darsteller
from utils.web_scapings.iafd.scrape_iafd_performer import ScrapeIAFDPerformer
from utils.web_scapings.iafd.update_iafd_performer import UpdateIAFDPerformer
from utils.web_scapings.theporndb.update_theporndb_performer import UpdateThePornDBPerformer 
from gui.context_menus.helpers.refresh_nameslink_table import RefreshNameslinkTable  
from gui.clearing_widgets import ClearingWidget
from gui.dialog_gender_auswahl import GenderAuswahl
from gui.dialog_performer_mask_selection import PerformMaskSelection
from gui.helpers.message_show import StatusBar, blink_label, MsgBox

from config import PROJECT_PATH, WEBINFOS_JSON_PATH

class DatenbankPerformerMaske():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow  
        logging.basicConfig(filename=PROJECT_PATH / "log_files" / 'log_updates.log', level=logging.INFO, 
            format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')      

    def artist_infos_in_maske(self): 
        iafd_infos=ScrapeIAFDPerformer(MainWindow=self.Main)
        db_scene_mask = DatenbankSceneMaske(MainWindow=self.Main)
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main) 
        data_mask = SetDatenInMaske(self.Main)   
        class_tooltip_text = SetTooltipText(self.Main) 
        clearing = ClearingWidget(self.Main)  

        self.Main.set_performer_maske_text_connect(disconnect=True)        
        clearing.clear_maske()
        self.clear_button_color()
        selected_row = self.get_selected_row_from_table('performer')
        artist_id = self.get_table_data(selected_row, 0)  
        ### --------- Name Überschrift setzen ------------------------- ###
        self.Main.grpBox_performer_name.setTitle(f"Performer-Info ID: {artist_id}")         
        self.Main.lnEdit_performer_info.setText(self.get_table_data(selected_row, 1).strip()) # Name
        self.Main.lnEdit_performer_ordner.setText(self.get_table_data(selected_row, 2).strip()) # Ordner            
        ### --------- Geschlechts QComboBox setzen -------------------- ###         
        gender_auswahl = GenderAuswahl(self.Main, False)        
        gender_auswahl.set_icon_in_gender_button(self.get_table_data(selected_row, 5))        
        ### --------- Rasse QComboBox setzen ------------------------- ### 
        self.set_rasse_in_combobox(artist_id, class_tooltip_text)        
        ### --------- Nation QComboBox setzen -- von englisch(DB) in deutsch(Maske) ------ ###        
        self.set_nations_in_labels(self.get_table_data(selected_row, 7), class_tooltip_text) 
        ### --------- Augenfarbe in ComboBox setzen ------------------- ###
        if self.get_table_data(selected_row, 18):
            self.set_eyecolor_in_combobox(self.get_table_data(selected_row, 18), class_tooltip_text)        
        ### --------- Fan Side/OnlyFans QComboBox setzen -------------- ###
        self.Main.set_social_media_in_buttons(self.get_table_data(selected_row, 10))
        ### --------- Quell Links in QTableWidget setzen -------------- ### 
        self.update_names_linksatz_in_ui(artist_id)  
        ### --------- IAFD Link setzen -------------------------------- ### 
        if self.get_table_data(selected_row, 3):            
            if self.get_table_data(selected_row, 3)=="N/A":
                self.Main.chkBox_iafd_enabled.setChecked(False) # IAFD feld deaktivieren                              
                self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(False)
            else:
                self.Main.chkBox_iafd_enabled.setChecked(True)
                self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)
                self.Main.lbl_checkWeb_IAFD_artistURL.setStyleSheet("background-image: url(':/labels/_labels/check.png')")
            data_mask.set_daten_in_maske("lnEdit_DB", "IAFD_artistLink", "Datenbank", self.get_table_data(selected_row, 3), artist=True)
        elif self.Main.chkBox_get_autom_iafd.isChecked():
             self.Main.lnEdit_create_iafd_link.setText(self.get_table_data(selected_row, 1))                      
             iafd_infos.get_IAFD_performer_link() 
             self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)         
        ### --------- Bio Website(u.a. BabePedia) Link setzen -------------------------------- ###
        if self.get_table_data(selected_row, 4):
            bio_sites = self.get_table_data(selected_row, 4).split("\n")                      
            self.set_bio_websites_tooltip(bio_sites)  
        ### ----------- Rest in Maske packen ------------ ###        
        self.update_all_edits_tooltips(selected_row, db_scene_mask)        
        ### ----------- IAFD Image in Label setzen ------- ###
        biowebsites = self.Main.get_bio_websites(True) + ["IAFD"]
        for biowebsite in biowebsites:
            self.set_biowebsite_image_in_label(biowebsite, artist_id, class_tooltip_text, datenbank_darsteller) 

    def set_biowebsite_image_in_label(self, site, artist_id, class_tooltip_text, datenbank_darsteller):
        image_pfad = datenbank_darsteller.get_biowebsite_image(site, artist_id)[1]
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            class_tooltip_text.set_tooltip_text("lbl_", f"{site.lower()}_image", f"Datenbank: '{image_pfad}'", "Datenbank")
            pixmap = QPixmap()
            pixmap.load(str(image_pfad))
            stacked = getattr(self.Main,f"stacked_{site.lower()}_label")
            self.Main.stacked_webdb_images.setCurrentWidget(stacked)
        else:
            class_tooltip_text.set_tooltip_text("lbl_", f"{site.lower()}_image", f"Datenbank: 'Kein Bild gespeichert'", "Datenbank")                              
            pixmap = QPixmap(":/labels/_labels/kein-bild.jpg")                   
        getattr(self.Main,f"lbl_{site.lower()}_image").setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))
        self.Main.set_performer_maske_text_connect(disconnect=False)        

    def set_bio_websites_tooltip(self, bio_sites: str):        
        clearing = ClearingWidget(self.Main) 
        for biosite in bio_sites:               
            for bio_name, bio_url in self.Main.get_bio_websites().items():                
                btn_widget = getattr(self.Main,f"Btn_performer_in_{bio_name}") # widget : url
                if biosite.startswith(bio_url):
                    clearing.set_website_bio_enabled([bio_name], True)
                    btn_widget.setToolTip(biosite)            

    def set_rasse_in_combobox(self, artist_id, class_tooltip_text):        
        database_darsteller = DB_Darsteller(self.Main)
        try:
            rassen_ids = database_darsteller.get_rassenids_from_artistid(int(artist_id))
        except ValueError:
            print(artist_id)
            rassen_ids=[]
        for rassen_id in rassen_ids:
            self.Main.cBox_performer_rasse.setChecked(rassen_id-1)         
        rasse=self.Main.cBox_performer_rasse.currentText()  
        class_tooltip_text.set_tooltip_text("cBox_performer_", "rasse", f"Datenbank: {rasse}", "Datenbank")

    def set_eyecolor_in_combobox(self, eye_colour, class_tooltip_text):
        index = self.Main.cBox_performer_eye.findText(eye_colour)
        if index >= 0: 
            self.Main.cBox_performer_eye.setCurrentIndex(index)
        else:
            self.Main.cBox_performer_eye.setCurrentIndex(0)
            eye_colour = f"{eye_colour} (nicht in der Liste)"
        class_tooltip_text.set_tooltip_text("cBox_performer_", "eye", f"Datenbank: {eye_colour}", "Datenbank")

    def set_nations_in_labels(self, nations: str, class_tooltip_text, art="Datenbank"):
        nations=nations.split(", ") if nations else ""
        datenbank_darsteller = DB_Darsteller(self.Main)
        for zahl, nation_ger in enumerate(nations):
            nation_shortsymbol=datenbank_darsteller.get_shortsymbol_from_german(nation_ger)
            if nation_shortsymbol==None:
                print(f"Nation '{nation_ger}' nicht in Datenbank gefunden")
            else:
                getattr(self.Main,f"lbl_performer_nation_{zahl}").setProperty("nation", nation_ger)            
                getattr(self.Main,f"lbl_performer_nation_{zahl}").setStyleSheet(f"background-image: url(:/labels/_labels/nations/{nation_shortsymbol.lower()}.png);")
                class_tooltip_text.set_tooltip_text(f"lbl_performer_nation_{zahl}", "", f"{art}: {nation_ger}", art)

    def get_social_media_from_buttons(self) -> str: 
        social_medias: str=""
        for index in range(10):
            social_media=getattr(self.Main, f"Btn_performers_socialmedia_{index}").toolTip().replace("Datenbank: ", "")
            if social_media:
                social_medias += social_media +"\n"
        return social_medias[:-1]
    
    def get_selected_row_from_table(self, widgetname):
        selected_indexes = getattr(self.Main, f"tblWdg_{widgetname}").selectedIndexes()
        if selected_indexes:
            selected_row = selected_indexes[0].row() 
        else:
            selected_row = -1
        return selected_row
    
    def get_bio_websites_from_buttons(self) -> str: # von allen links ein datenbank eintrag
        bio_websites: str=""
        for biowebsite in self.Main.get_bio_websites(widget=True):
            bio_website = getattr(self.Main, f"Btn_performer_in_{biowebsite}").toolTip()
            if bio_website:
                bio_websites += bio_website +"\n"
        return bio_websites[:-1]

    def get_artistdata_from_ui(self, artist_id, database: bool=False) -> Tuple[dict, list]:
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)        
        ### -------------- Geschlecht für update vorbereiten ------------------ ###        
        gender_auswahl = GenderAuswahl(self.Main, False)
        gender = gender_auswahl.get_gender_from_button()        
        ### -------------- RassenID für update vorbereiten -------------------- ### 
        rassen = "/".join(self.Main.cBox_performer_rasse.get_checked_items()) 
        
        ### -------------- Nation für update vorbereiten ----------------------- ###         
        nations = self.get_nations_from_labels()         
        ### -------------------------------------------------------------------- ###
        daten_satz = {
            "ArtistID" : int(artist_id),
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
            "Augenfarbe": self.Main.cBox_performer_eye.currentText(),
            "Aktiv": self.Main.lnEdit_performer_activ.text().strip(),
            "ThePornDB": self.Main.Btn_performer_in_ThePornDB.toolTip(),
            "FakeBoobs": 1 if self.Main.chkBox_fake_boobs.isChecked() else 0,    }
        names_link_satz = []
        if database:            
            names_link_satz=self.nameslink_datensatz_in_dict(names_link_satz)                     
        return daten_satz, names_link_satz
    
    def update_all_edits_tooltips(self, selected_row, db_scene_mask):
        lineedit_dict = {"birthday":8,
                     "birthplace":9,
                     "boobs": 11,
                     "weight": 12,
                     "height": 13,
                     "body": 14,                     
                     "hair": 17,
                     "activ": 19}
        textedit_dict = {"piercing": 15,
                         "tattoo": 16}
        for actor_type, column in lineedit_dict.items(): 
            value = self.get_table_data(selected_row, column)         
            db_scene_mask.set_daten_with_tooltip("lnEdit_performer_", actor_type, "Datenbank", value, artist=True)
        for actor_type, column in textedit_dict.items():
            value = self.get_table_data(selected_row, column)
            db_scene_mask.set_daten_with_tooltip("txtEdit_performer_", actor_type, "Datenbank", value, artist=True)


    def get_table_data(self, row, column):
        index = self.Main.tblWdg_performer.model().index(row, column) 
        return self.Main.tblWdg_performer.model().data(index)  
    
    def get_nations_from_labels(self) -> str:
        nations: str = []
        for zahl in range(7): 
            nation = getattr(self.Main,f"lbl_performer_nation_{zahl}").property("nation") 
            if nation:
                nations.append(nation)
        return ", ".join(nations)
    
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
    
    def put_daten_satz_in_tablewidget(self, artist_id): 
        daten_satz,_ = self.get_artistdata_from_ui(artist_id)
        
        items = self.Main.tblWdg_performer.findItems(str(artist_id), Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchFixedString) 
        if items:
            selected_row = items[0].row()
        else:
            return 0, -1
        del daten_satz['ThePornDB'] # den letzten item löschen
        for spalte, (key, value) in enumerate(daten_satz.items()):
            self.Main.tblWdg_performer.setItem(selected_row, spalte, QTableWidgetItem(f"{value}"))            
            self.Main.tblWdg_performer.selectRow(selected_row)
        self.Main.tblWdg_performer.update()
        return selected_row               

    def update_datensatz(self):
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)        

        self.Main.Btn_DBArtist_Update.setEnabled(False) 
        message: str=""
        #### -------------------------------------------------------------- #### 
        artist_id = self.Main.grpBox_performer_name.title().replace("Performer-Info ID: ","")
        selected_row = self.put_daten_satz_in_tablewidget(artist_id)
        if selected_row > -1:
            message = self.update_dataset_in_database(artist_id, selected_row, datenbank_darsteller) 
        else:
            message = "❌ID nicht gefunden !"
        ### ------------ Message Ausgabe ----------------------------------- ###
        self.Main.txtBrowser_loginfos.append(message)
        self.Main.txtBrowser_loginfos.verticalScrollBar().setSliderPosition(self.Main.txtBrowser_loginfos.verticalScrollBar().maximum()) 
        logging.info(message)
        self.Main.lbl_db_status.setText(message)
        self.Main.Btn_DBArtist_Update.setEnabled(False)

    def update_dataset_in_database(self, artist_id, selected_row, datenbank_darsteller):
        update_iafd_performer = UpdateIAFDPerformer(self.Main, self)
        update_theporndb_performer = UpdateThePornDBPerformer(self.Main, self)
        ordner = self.Main.lnEdit_performer_ordner.text()
        errview = {}
        message = {}   
        ### -------------- IAFD Image und andere Images werden gespeichert --------------------------- ###          
        message, errview  = update_iafd_performer.save_iafd_image_in_datenbank(message, errview, datenbank_darsteller, artist_id)
        ### -------------- The Porn DB Image und andere Images werden gespeichert --------------------------- ###          
        message, errview  = update_theporndb_performer.save_theporndb_image_in_datenbank(message, errview, datenbank_darsteller, artist_id)
        ### -------------- Rasse updaten ------------------------------------------------------------- ###
        rassen = "/".join(self.Main.cBox_performer_rasse.get_checked_items())
        message, errview = self.update_rassen(message, errview, rassen, artist_id, datenbank_darsteller)
        ### -------------- Nation updaten ------------------------------------------------------------ ### 
        message, errview = self.update_nations(message, errview,  self.get_nations_from_labels(), artist_id, datenbank_darsteller)
        ### -------------- Performer updaten --------------------------------------------------------- ###
        daten_satz_ui, names_link_satz_ui = self.get_artistdata_from_ui(artist_id, database=True) 
        ### -------------- Update was in der Tabelle von Performer_Links drin ist -------------------- ###
        is_neu_linksatz, is_update_linksatz = self.update_and_check_names_linksatz_for_db(names_link_satz_ui, artist_id, datenbank_darsteller) 
        if (is_neu_linksatz or is_update_linksatz) > 0:
            self.update_names_linksatz_in_ui(artist_id)                     
        ### ------------ Check auf Veränderungen in der datenbank Maske für Performer Liste ---------- ###
        message, errview = self.update_performer_datensatz_for_db(message, errview,  daten_satz_ui, artist_id, datenbank_darsteller)         
        self.refresh_nameslink_table = RefreshNameslinkTable(self.Main, self)
        self.refresh_nameslink_table.refresh_performer_links_tabelle()    
        return self.merge_messages(message, errview, selected_row) 

    def update_nations(swlf, message, errview, nations_ger: str, artist_id: int, datenbank_darsteller) -> str:
        nations_ids: list = []

        for nation_german in nations_ger.split(", "):
            id = datenbank_darsteller.get_nations_id_from_nations_ger(nation_german)
            if id >-1:                
                nations_ids.append(id)
        errview['nation'], is_addet = datenbank_darsteller.update_or_add_nation_datensatz(nations_ids, artist_id)
        if not errview['nation']:
            if is_addet:
                message['nation'] = ".➕Nationen wurde geaddet/updated/gelöscht"
                errview['nation'] = None 
        else:
            errview['nation'] = f".❌Fehler beim Nation Adden: {errview['nation']}"
            message['nation'] = None 
        return message, errview
    
    def update_rassen(self, message, errview, rassen_ger: str, artist_id: int, datenbank_darsteller) -> str:        
        rassen_ids: list = []        

        for rasse_german in rassen_ger.split("/"):
            id = datenbank_darsteller.get_rassen_id_from_rassen_ger(rasse_german)
            if id >-1: 
                rassen_ids.append(id)
        errview['rasse'], is_addet = datenbank_darsteller.update_or_add_rassen_datensatz(rassen_ids, artist_id)
        if not errview['rasse']:
            if is_addet:
                message['rasse'] = ". Eine Rasse wurde geaddet/updated/gelöscht" 
                errview['rasse'] = None                       
        else:
            message['rasse'] = None 
            errview['rasse'] = f". Fehler beim Rasse Adden: {errview['rasse']}"            
        return message, errview

    ### ------------------- speichert Link, Image, Alias in die Datenbank ------------------ ###    
    def update_performer_datensatz_for_db(self, message, errview, datensatz_ui, artist_id, datenbank_darsteller):
        is_update: bool=False

        datensatz_db = datenbank_darsteller.get_performer_dataset_from_artistid(artist_id)
        if datensatz_db[0]: 
            diff = set(datensatz_db[0].items()) ^ set(datensatz_ui.items())           
            if set(datensatz_db[0].values()) != set(datensatz_ui.values()): # Datenbank mit UI vergleichen
                errview['datensatz'], is_update = datenbank_darsteller.update_performer_datensatz(datensatz_ui)
                if is_update:
                    diff_dict = {}
                    for key, value in diff:
                        diff_dict[key] = diff_dict.get(key, ()) + (value,)
                    for key, (val1, val2) in diff_dict.items():
                        print(f"Schlüssel {key} sind die Werte unterschiedlich: {val1} != {val2}")
                    message['datensatz'] = f", Datensatz in >{len(diff_dict)}< Werte geändert"
                    errview['datensatz'] = None
                else:
                    message['datensatz'] = None
                    errview['datensatz'] = ", Datensatz nicht updated"
            else:
                message['datensatz'] = ", Datensatz hat keine Veränderung"
                errview['datensatz'] = None
        return message, errview 
    
    def update_and_check_names_linksatz_for_db(self, names_link_satz_ui, artist_id, datenbank_darsteller):
        is_neu_datensatz: int=0
        is_update_datensatz: int=0
        
        for linksatz in names_link_satz_ui:
            url = linksatz["Link"]
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
    
    def merge_messages(self, message, errview, selected_row):
        db_scene_mask = DatenbankSceneMaske(MainWindow=self.Main)
        msg = ""
        for key, value in errview.items():
            if value:
                msg += f"❌{value}, "
                blink_label(self.Main, "lbl_db_status", "#FF0000")        
        for key, value in message.items():
            if value:
                msg += f"✅{value}, "
                blink_label(self.Main, "lbl_db_status", "#55ff7f")          
        self.update_all_edits_tooltips(selected_row, db_scene_mask)
        self.clear_button_color()                     
        return msg.strip(", ") # letztes Komma entfernen

    def clear_button_color(self):
        clearing_widget = ClearingWidget(self.Main)
        clearing_widget.invisible_performer_btn_anzahl()
        widgets = clearing_widget.performers_tab_widgets("lineprefix_perf_textprefix_perf_lineiafd")
        widgets.extend(clearing_widget.performers_tab_widgets("combo_perf"))
        for widget in widgets: # masken farbe wieder bereinigen bei erfolgreichen update
            self.Main.set_color_stylesheet(widget, color_hex='#FFFDD5')   
        
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

            iafd_infos = ScrapeIAFDPerformer(MainWindow=self.Main)
            iafd_url=self.Main.lnEdit_DBIAFD_artistLink.text()
            artist_id = self.Main.grpBox_performer_name.title().replace("Performer-Info ID: ","")
            name = self.Main.lnEdit_performer_info.text()

            iafd_infos.load_IAFD_performer_link(iafd_url, artist_id, name) # scrape IAFD infos
            if Path(WEBINFOS_JSON_PATH).exists() and json.loads(WEBINFOS_JSON_PATH.read_bytes()):           
                self.set_iafd_infos_in_ui() # setzt die scraped infos in die DB Maske
                self.update_datensatz() # und speichert alles in die Datenbank
        MsgBox(self.Main,"Fertig !","i")

    def setinfo_label(self,now_iafd, iafd,now_bio,bio_infos,current_iafd,no_infos, table_performer_count):
        self.Main.lbl_infos_on_imagestacked.setText(f"IAFD: {now_iafd}|{iafd} / kein IAFDLink: {now_bio}|{bio_infos} / durchsuche: {current_iafd}|{no_infos} gesamt: {table_performer_count}")   
           
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
        if not Path(Path(image_path).parent).exists():
            Path(Path(image_path).parent).mkdir(parents=True)
        pixmap.save(str(image_path), "JPEG")
    #### ----------------------------------------------------------------------------- ####
        
    def is_ein_bild_dummy_im_label(self, widget):
        kein_bild_vorhanden_image_path = ":/labels/_labels/kein-bild.jpg" 
        kein_bild_vorhanden_image = QPixmap(str(kein_bild_vorhanden_image_path)).toImage()        
        # Lade das aktuelle Bild im Label
        current_image = getattr(self.Main,f"lbl_{widget}_image").pixmap().toImage() if getattr(self.Main,f"lbl_{widget}_image").pixmap() else None 
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
            GenderAuswahl(self.Main, False).set_icon_in_gender_button(str(sex)) 
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
            tool_text=SetTooltipText(MainWindow=self.Main)
            self.set_nations_in_labels(nations_ger, tool_text, "IAFD")
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
        id = self.Main.grpBox_performer_name.title().replace("Performer-Info ID: ","") # ArtistID
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
            try:
                button.clicked.disconnect()
            except TypeError:
                pass 
            button.clicked.connect(lambda state, btn=label.objectName():PerformMaskSelection(self.Main, btn).exec())          

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
    DatenbankPerformerMaske()