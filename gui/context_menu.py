from PyQt6 import uic
from PyQt6.QtWidgets import QMenu, QTableWidgetItem, QWidget 
from PyQt6.QtGui import QAction, QCursor, QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer, QCoreApplication, pyqtSignal

import functools
import json
import winreg
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from typing import Tuple
import errno

from gui.performer_add_del_dialog import PerformerAddDel
from utils.database_settings.database_for_settings import Webside_Settings, SettingsData
from utils.web_scapings.iafd.update_iafd_performer import UpdateIAFDPerformer
from utils.web_scapings.datenbank_scene_maske import DatenbankSceneMaske
from utils.web_scapings.iafd.scrape_iafd_scene import ScrapeIAFDScene
from utils.web_scapings.iafd.scrape_iafd_performer import ScrapeIAFDPerformer
from utils.web_scapings.data18.scrape_data18_scene import ScrapeData18Scene
from gui.helpers.set_tootip_text import SetTooltipText
from utils.helpers.check_biowebsite_status import CheckBioWebsiteStatus
from utils.web_scapings.scrap_with_requests import VideoUpdater
from utils.database_settings.database_for_darsteller import DB_Darsteller
from utils.web_scapings.load_performer_images_from_websites import LoadPerformerImages
from utils.web_scapings.datenbank_performer_maske import DatenbankPerformerMaske
from gui.context_menus.helpers.refresh_nameslink_table import RefreshNameslinkTable


from gui.helpers.message_show import MsgBox, StatusBar, blink_label

from config import MEDIA_JSON_PATH
from config import LOESCH_DIALOG_UI, RENAME_DIALOG_UI, DATEI_AUSWAHL_UI, PROJECT_PATH, ADD_PERFORMER_UI, ICON_PATH
import gui.resource_collection_files.labels_rc

class ContextMenu(QMenu):
    add_name_and_ordner=pyqtSignal(str, str, int)    
    merge_ids=pyqtSignal(int,int)
    add_artist=pyqtSignal(int, str, str, str) # artist_id, iafd_link, name
    add_namesid=pyqtSignal(int, dict, int) # artist_id, names_link_satz, studio_id
    def __init__(self, parent = None):
        super().__init__()
        self.Main = parent        
        self.dialog_shown = False        
        self.add_name_and_ordner.connect(self.perfomer_add_resultsignal) 
        self.merge_ids.connect(self.merge_performer_resultsignal) 
        self.add_artist.connect(self.add_performer_from_link_resultsignal)
        self.add_namesid.connect(self.add_namesid_from_link_resultsignal) 
    ### --------------------------------------------------------------------- ###
    ### ------Pushup Menu inder Tabelle ------------------------------------- ###
    ### --------------------------------------------------------------------- ###
    def showContextMenu(self, pos: int, widget_name) -> None:
        current_widget = self.sender()        
        if current_widget:
            widget_actions = {
                self.Main.tblWdg_performer: self.showContextMenu_in_performer_search,
                self.Main.tblWdg_files: self.showContextMenu_in_Files,
                self.Main.txtEdit_DBSynopsis: self.showContextMenu_in_Synopsis,
                self.Main.txtEdit_DBTags: self.showContextMenu_in_DBTags,
                self.Main.tblWdg_performer_links: self.showContextMenu_in_performer_links,
                self.Main.tblWdg_DB_performers: self.showContextMenu_in_scene_performers               
            }
            action = widget_actions.get(current_widget)
            if action:
                action(current_widget.mapToGlobal(pos))

#### ------------- Aufruf für die 'Scene Performer Tabelle' ------------------------------ #####
    def showContextMenu_in_scene_performers(self, pos: int) -> None: # tblWdg_DB_performers
        if self.Main.tblWdg_performer_links.horizontalHeaderItem(0):            
            action_header: QAction = self.set_header_on_contextmenu("Tabelle Scene Performer")
            menu_dict: dict = {
                "lade Performer Infos": ("ContexMenu/actor_info.png", self.load_actor_infos),                 }
            self.show_context_menu(pos, action_header, menu_dict)
    
    def load_actor_infos(self):
        actorname = self.Main.tblWdg_DB_performers.item(self.Main.tblWdg_DB_performers.currentRow(), 0).text()
        self.Main.customlnEdit_IAFD_performer.setText(actorname)
        tab = self.Main.tabs.findChild(QWidget, 'tab_performer')
        self.Main.tabs.setCurrentIndex(self.Main.tabs.indexOf(tab))
        page = self.Main.stacked_tables.findChild(QWidget, 'page_table_performer')
        self.Main.stacked_tables.setCurrentIndex(self.Main.stacked_tables.indexOf(page))
        self.Main.datenbank_performer_suche()
#### ----------- Aufruf für die 'Performer Links Tabelle' ------------------------------ #####
    def showContextMenu_in_performer_links(self, pos: int) -> None: # tblWdg_performer_links
        action_header: QAction = self.set_header_on_contextmenu("Tabelle Performer Links")
        menu_dict: dict = {
            "Zeile hinzufügen": ("zeile_add.png", lambda: PerformerAddDel(self, menu="add_new_nameslink", Main=self.Main) if not self.dialog_shown else None),
            "Zeile löschen": ("zeile_del.png", self.delete_item),
            "Zeile für eine neuen Performer Datensatz anlegen": ("new_database.png", lambda: PerformerAddDel(self, menu="add_new_performer", Main=self.Main) if not self.dialog_shown else None), 
            "Refresh Tabelle neu aus Datenbank": ("load_table.png", self.refresh_performer_links_tabelle),
            "Lade Bild von Website": ("load_image.png", self.load_image_from_webside),
            "Tabellenspalten am Text anpassen": ("table_content.png", self.context_resize),
            "Explorer im Namen Ordner öffnen": ("explorer.png", self.open_explorer)     }
        self.show_context_menu(pos, action_header, menu_dict)
#### ---------------------------------------------------------------------------------- #####    
#### ----------------- Aktionen in der 'Performer Links Tabelle' ---------------------- ##### 
#### ---------------------------------------------------------------------------------- #####  
    ### -------------------------- Zeile hinzufügen --------------------------------- ### 
    def add_namesid_from_link_resultsignal(self, artist_id, names_link_satz, studio_id):
        is_vorhanden=False                
        for row in range(self.Main.tblWdg_performer_links.rowCount()):
            if self.Main.tblWdg_performer_links.item(row, 0).text() == names_link_satz["NamesID"]:
                is_vorhanden=True
                break
        if is_vorhanden == False:
            datenbank_performer_maske = DatenbankPerformerMaske(self.Main)
            row_count = self.Main.tblWdg_performer_links.rowCount()
            self.Main.tblWdg_performer_links.setRowCount(row_count+1)
            self.Main.tblWdg_performer_links.setItem(row_count, 0, QTableWidgetItem(f'{names_link_satz["NamesID"]}'))
            self.Main.tblWdg_performer_links.setItem(row_count, 1, QTableWidgetItem(f'{names_link_satz["Link"]}'))
            self.Main.tblWdg_performer_links.setItem(row_count, 2, QTableWidgetItem(f'{names_link_satz["Image"]}'))
            self.Main.tblWdg_performer_links.setItem(row_count, 3, QTableWidgetItem(f'{names_link_satz["Alias"]}'))
            datenbank_performer_maske.setColortoRow(self.Main.tblWdg_performer_links,row_count,'#FFFD00')
            datenbank_performer_maske.set_icon_in_tablewidget(row_count, names_link_satz["Image"]) 
        self.Main.tblWdg_performer_links.resizeColumnsToContents()

    def refresh_performer_links_tabelle(self):
        datenbank_performer_maske = DatenbankPerformerMaske(self.Main)
        refresh_nameslink_table = RefreshNameslinkTable(self.Main, datenbank_performer_maske)
        refresh_nameslink_table.refresh_performer_links_tabelle()    
    ### -------------------------- Zeile löschen --------------------------------- ### 
    def delete_item(self):
        name=self.Main.lnEdit_performer_info.text()
        if self.Main.tblWdg_performer_links.rowCount()>-1 and name:        
            row_index = self.Main.tblWdg_performer_links.currentRow()
            if row_index >= 0 and self.Main.tblWdg_performer_links.item(row_index, 0).isSelected():
                datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
                names_id=self.Main.tblWdg_performer_links.selectedItems()[0].text()                
                is_delete = datenbank_darsteller.delete_nameslink_satz(names_id) 
                if is_delete:
                    path=self.Main.tblWdg_performer_links.selectedItems()[2].text() 
                    ordner=self.Main.lnEdit_performer_info.text()                  
                    if path.startswith("__artists_Images/{ordner}/") and Path(PROJECT_PATH / path).exists():
                        Path(PROJECT_PATH / path).unlink()                                       
                    is_empty_dir=Path(Path(PROJECT_PATH / path).parent)
                    if is_empty_dir.is_dir() and not any(is_empty_dir.iterdir()): # leeres Verzeichnis löschen                    
                        is_empty_dir.rmdir()
                    if self.Main.tblWdg_performer_links.selectedItems()[1].text().startswith("https://www.iafd.com/person.rme/perfid="):
                        pixmap = QPixmap(":/labels/_labels/kein-bild.jpg")                   
                        self.Main.lbl_iafd_image.setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))
                        self.Main.lbl_iafd_image.setToolTip("")
                    self.Main.lbl_link_image_from_db.clear()
                    self.Main.lbl_link_image_from_db.setToolTip("")
                    self.Main.lbl_performer_link.setText("")
                    self.Main.tblWdg_performer_links.removeRow(row_index)
                    self.refresh_performer_links_tabelle()
                    self.Main.lbl_db_status.setText(f"Zeile: {row_index+1} mit der ID: {names_id} wurde auch aus der Datenbank gelöscht !")
                    self.Main.Btn_DBArtist_Update.setEnabled(True)
                else:
                    StatusBar(self.Main,"Fehler beim Löschen der ID !","#FF0000")
            else:
                self.Main.lbl_db_status.setText("Keine Zeile ausgewählt !")
                blink_label(self.Main, "lbl_db_status" ,"#FF0000")
                QTimer.singleShot(3000, lambda :self.Main.lbl_db_status.setText("")) 
        else:
            StatusBar(self.Main,"Kein Name oder nichts in der Tabelle drin !","#FF0000")
    
    ### ----------------- Zeile für eine neuen Performer Datensatz anlegen ------------------------ ### 
    def add_performer_from_link_resultsignal(self, artist_id: int, iafd_link, name, ordner):
        is_updated: int=0         
        message = ""	     
        iafd_msg = "" 
        links = []
        zeilen = []
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)

        for zeile in range(self.Main.tblWdg_performer_links.rowCount()): # check welche Zeilen ausgewählt sind
            item = self.Main.tblWdg_performer_links.item(zeile, 0) # NamesID 
            if item and item.isSelected():
                if iafd_link:
                    msg, is_update=self.update_performer_from_iafd_link(artist_id, iafd_link, name, ordner, datenbank_darsteller)
                    is_updated +=is_update 
                    iafd_msg ="(incl IAFD)"
                    message += f"<tr><td>{msg}</td></tr>"                  
                errview, is_update = datenbank_darsteller.update_artistid_from_names_id(f"{item.text()}", artist_id)
                is_updated += is_update 
                zeilen.append(zeile)               
                links.append(self.Main.tblWdg_performer_links.item(zeile, 1).text())                
        for zeile in zeilen:
            self.Main.tblWdg_performer_links.removeRow(zeile)
        message += f"<tr><td>{is_updated} Links {iafd_msg} sind verschoben worden</td></tr>"        
        artist_data = datenbank_darsteller.get_performer_dataset_from_artistid(artist_id) 
        keys_to_include = ['ArtistID', 'Name', 'Ordner']
        filtered_data = {key: artist_data[0][key] for key in keys_to_include}         
        message += f"<tr><td>{', '.join(map(str, filtered_data.values()))}<td><th>"        
        MsgBox(self, f"<table border='1'><tr><th>  Performer hinzugefügt  </th></tr>{message}</table>","i")

    def update_performer_from_iafd_link(self, artist_id: int, iafd_link: str, name: str, ordner: str, datenbank_darsteller):    
        iafd_artist_id = datenbank_darsteller.get_artistid_from_nameslink(iafd_link)
        if iafd_artist_id != -1: # kein iafd link gefunden, neu anlegen
            return "IAFD Link schon da", 0
        else:
            iafd_infos = ScrapeIAFDPerformer(MainWindow=self.Main)
            iafd_infos.load_IAFD_performer_link(iafd_link, str(iafd_artist_id), name) # IAFD daten von der website scrapen 
            datenbank_performer_maske = DatenbankPerformerMaske(self.Main)
            update_iafd_performer = UpdateIAFDPerformer(self.Main)
            message = datenbank_performer_maske.update_iafd_datensatz_from_json(artist_id, ordner) # performer update with iafd datas
            perfid = update_iafd_performer.get_perfid_from_iafd_link(iafd_link)
            update_iafd_performer.names_link_from_iafd(ordner, perfid, iafd_link, artist_id, datenbank_darsteller) # iafd names datensatz neu anlegen
            return message, 1  
    ### ------------------------------------------------------------------------------------------- ###
    

    ### ------------------------------------------------------------------------------------------- ###
            
    ### --------------------- Lade Bild von Website ----------------------------------------------- ###
    def load_image_from_webside(self):
        ordner=self.Main.lnEdit_performer_ordner.text()
        if self.Main.tblWdg_performer_links.rowCount()>-1 and ordner:
            current_row = self.Main.tblWdg_performer_links.currentRow()            
            item = QTableWidgetItem() 
            item.setIcon(QIcon(':/labels/_labels/sanduhr.gif'))           
            self.Main.tblWdg_performer_links.setItem(current_row,4,item)
            pixmap = QPixmap(":/labels/_labels/waiting.jpg")                    
            self.Main.lbl_link_image_from_db.setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))
            QCoreApplication.processEvents()
            load = LoadPerformerImages(MainWindow=self.Main, ordner=ordner)            
            load.load_website_image_in_label()
            item = self.Main.tblWdg_performer_links.item(current_row, 4)
            item.setIcon(QIcon(':/labels/_labels/check.png'))            
        else:
            self.Main.lbl_db_status.setText("Kein Name oder nichts in der Tabelle drin !")            
    ### ------------------------------------------------------------------------------------------- ###
            
    ### ---------------------- Tabellespalten am Text anpassen ------------------------------------ ###        
    def context_resize(self):
        self.Main.tblWdg_performer_links.resizeColumnsToContents()
        self.Main.tblWdg_performer_links.update()
    ### ------------------------------------------------------------------------------------------- ###
        
    ### ---------------------- Explorer im Namen Ordner öffnen ------------------------------------ ### 
    def open_explorer(self):
        folder = Path(PROJECT_PATH / "__artists_Images" / self.Main.lnEdit_performer_ordner.text())
        if Path(folder).exists():
            subprocess.Popen(['explorer', str(folder)])
        else:
            self.Main.lbl_db_status.setText(f"Kein Ordner: '{self.Main.lnEdit_performer_ordner.text()}' vorhanden")
            blink_label(self.Main, "lbl_db_status", "#ff0000")
    ###################################################################################################  

    def showContextMenu_in_DBSceneCode(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Scene Code !")       
        menu_dict=self.action_links(self.scrap_scenecode)
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_DBTags(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Tags !")       
        menu_dict= self.action_links(self.scrap_tags)
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_DBProDate(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Productions Datum !")       
        menu_dict= self.action_links(self.scrap_prodate)
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_Synopsis(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Synopsis !")       
        menu_dict = self.action_links(self.scrap_synopsis)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = ("data18_20.png", functools.partial(self.scrap_synopsis, self.Main.lnEdit_DBData18Link.text()))
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = ("iafd_20.png", functools.partial(self.scrap_synopsis,self.Main.lnEdit_DBIAFDLink.text()))
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_regie(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Regieseur !")       
        menu_dict = self.action_links(self.scrap_regie)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = ("data18_20.png", functools.partial(self.scrap_regie, self.Main.lnEdit_DBData18Link.text()))
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = ("iafd_20.png", functools.partial(self.scrap_regie,self.Main.lnEdit_DBIAFDLink.text()))
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_serie(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Serie/Unter-Studio !")       
        menu_dict = self.action_links(self.scrap_serie)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = ("data18_20.png", functools.partial(self.scrap_serie, self.Main.lnEdit_DBData18Link.text()))
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = ("iafd_20.png", functools.partial(self.scrap_serie,self.Main.lnEdit_DBIAFDLink.text()))
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_release(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Release Datum !")       
        menu_dict = self.action_links(self.scrap_release)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = ("data18_20.png", functools.partial(self.scrap_release, self.Main.lnEdit_DBData18Link.text()))
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = ("iafd_20.png", functools.partial(self.scrap_release,self.Main.lnEdit_DBIAFDLink.text()))
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_movies(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Movies und Alias !")       
        menu_dict=self.action_links(self.scrap_movies)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = ("data18_20.png", functools.partial(self.scrap_movies, self.Main.lnEdit_DBData18Link.text()))
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = ("iafd_20.png", functools.partial(self.scrap_movies,self.Main.lnEdit_DBIAFDLink.text()))
        self.show_context_menu(pos, action_header, menu_dict)

    def show_context_menu(self, pos: int, action_header: QAction, menu_dict: dict) -> None:
        if self.dialog_shown == False:
            self.context_menu = QMenu(self.Main)            
            self.context_menu.addAction(action_header)                          
            for menu, (icon, func) in menu_dict.items():                
                action = QAction(QIcon(f":/labels/_labels/{icon}"), menu, self.Main)            
                action.triggered.connect(func)                
                self.context_menu.addAction(action) 
            self.context_menu.setStyleSheet("QMenu::item:disabled {background: transparent;}")
            self.context_menu.exec(QCursor.pos())

    def set_header_on_contextmenu(self, header: str) -> QAction:
        action_readonly = QAction(header, self)
        font = action_readonly.font()
        font.setBold(True)       
        action_readonly.setFont(font)        
        action_readonly.setEnabled(False) 
        return action_readonly 

    def action_links(self, scraper_function) -> dict:        
        menu_dict = {} 
        icon="www.png"       
        for index in range(self.Main.model_database_weblinks.rowCount()):
            link = self.Main.model_database_weblinks.data(self.Main.model_database_weblinks.index(index, 0))
            web_link = urlparse(link).netloc
            menu_dict[web_link] = (icon, functools.partial(scraper_function, link))           
        return menu_dict

#### ----------- Aufruf für die 'Performer Namen Datenbank Such Tabelle' ----------- #####
    def showContextMenu_in_performer_search(self, pos: int) -> None: # tblWdg_performer        
        action_header: QAction = self.set_header_on_contextmenu("Tabelle Performer Suche") 
        menu_dict: dict = {
            "Zeile/Namen hinzufügen": ("name_hinzufuegen.png", lambda: PerformerAddDel(self, Main=self.Main) if not self.dialog_shown else None),
            "Zeile/Namen löschen": ("name_loeschen.png", self.delete_performer),
            "Zeile/Namen zusammenfügen/mergen mit ID": ("merge_person.png", lambda: PerformerAddDel(self, menu="merge", Main=self.Main) if not self.dialog_shown else None) }
        self.show_context_menu(pos, action_header, menu_dict)

#### ----------- Aktionen in dem 'Menu: Performer Tabelle' ------------------------------------- #####
#### ------------------------------------------------------------------------------------------- #####
    ### ------------------------ Zeile/Name hinzufügen ----------------------------- ###
    def perfomer_add_resultsignal(self, name: str, ordner: str, sex: int):        
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        performer_data={"Name": name,
                        "Ordner": ordner,
                        "Geschlecht": sex,
                        "Nation": None,
                        "ArtistLink": None,
                        "ImagePfad": None}
        errview, artist_neu, sex_neu, link_neu, new_artist_id = datenbank_darsteller.addDarsteller_in_db(performer_data)
        if new_artist_id != 0:            
            current_row = self.Main.tblWdg_performer.currentRow()
            new_row = current_row + 1
            self.Main.tblWdg_performer.insertRow(new_row)
            for column, header in enumerate(self.Main.get_header_for_performers_table()):
                if header == "ArtistID":
                    self.Main.tblWdg_performer.setItem(new_row, column, QTableWidgetItem(f'{new_artist_id}'))
                elif header == "Name":
                    self.Main.tblWdg_performer.setItem(new_row, column, QTableWidgetItem(name))
                elif header == "Ordner":
                    self.Main.tblWdg_performer.setItem(new_row, column, QTableWidgetItem(ordner))
                elif header == "Geschlecht":
                    self.Main.tblWdg_performer.setItem(new_row, column, QTableWidgetItem(f'{sex}'))
                else:
                    # Setzen Sie einen leeren String für alle anderen Spalten
                    self.Main.tblWdg_performer.setItem(new_row, column, QTableWidgetItem(""))            
            StatusBar(self.Main,f"{artist_neu} Datensatz wurde neu hinzugefügt","#3ADF00")
        else:
            if errview:
                StatusBar(self.Main,f"Fehler beim Datensatz adden: '{errview}'","#FF0000")
            elif sex_neu!=0:
                StatusBar(self.Main,"Fehler beim Datensatz adden: 'Den Ordner/Namen gibt es schon !'","#FF0000")
            else:
                StatusBar(self.Main,"Fehler beim Datensatz adden: 'Verschiedene Ordner angeben !'","#FF0000")
        QTimer.singleShot(1000, lambda :self.Main.statusBar.setStyleSheet('background-color:')) 

    ### ------------------------ Zeile/Namen löschen ------------------------------------------------ ###
    def delete_performer(self):        
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
        artist_id = self.Main.tblWdg_performer.selectedItems()[0].text()
        is_delete = datenbank_darsteller.delete_performer_dataset(artist_id)
        if is_delete:
            StatusBar(self.Main,f"Datensatz mit der Performer ID: {artist_id} erfolgreich gelöscht !","#3ADF00")
        else:
            performer_dataset=datenbank_darsteller.get_nameslink_dataset_from_artistid(artist_id)
            if performer_dataset:
                StatusBar(self.Main,"Einträge in der Performer Links Tabelle verhindern das Löschen !","#FF0000")
            else:
                StatusBar(self.Main,f"Fehler beim Löschen der Performer ID: {artist_id} !","#FF0000")
        self.Main.datenbank_performer_suche()        
        QTimer.singleShot(3000, lambda :self.Main.statusBar.setStyleSheet('background-color:'))

    
    ### ----------------------- Zeile/Namen zusammenfügen / Mergen mit ID --------------------------- ###
    def merge_performer_resultsignal(self, first_artist_id, artist_id):
        self.context_menu.close()
        del self.context_menu
        datenbank_darsteller = DB_Darsteller(self.Main) 
        datenbank_performer_maske = DatenbankPerformerMaske(self.Main) 
        message: str="" 
        names_link_satz = []        
        if self.Main.lnEdit_performer_info.text()=="":
            datenbank_performer_maske = DatenbankPerformerMaske(MainWindow=self.Main)
            datenbank_performer_maske.artist_infos_in_maske()        
        list_source_2 = datenbank_darsteller.get_quell_links(artist_id)
        if list_source_2 == [[], [], [], []]:
            message += self.delete_old_artist_id(artist_id, datenbank_darsteller)
            MsgBox(self, f"<table border='1'><tr><th>  Performer Link Tabelle  </th></tr>{message}</table>","i")
            return
        dict_source = datenbank_performer_maske.nameslink_datensatz_in_dict(names_link_satz)
        list_source_1 = self.from_dict_to_list(dict_source)        
        data_source_1 = self.database_to_dict(*list_source_1)
        data_source_2 = self.database_to_dict(*list_source_2)
        if (data_source_1 and data_source_2):           
            merge_link_satz = self.merge_ids_datas(data_source_2, data_source_1)
            new_ids, update_ids=self.get_new_and_updated_ids(list_source_1, list_source_2)            
            for id, link, image, alias in zip(*merge_link_satz):
                new_image= self.replace_folder(image)
                link_satz=self.nameslink_list_to_dict(id, link, new_image, alias)
                if id in new_ids:
                    studio_id=self.get_studio_id_from_link(link, datenbank_darsteller)                                        
                    is_neu = datenbank_darsteller.update_performer_names_link(first_artist_id, link_satz, studio_id)                    
                    if is_neu:
                        message += f"<tr><td>Update ID: {link_satz['NamesID']} {link_satz['Image']}</td></tr>"
                        position = list_source_2[0].index(id) 
                        old_file = list_source_2[2][position]
                        if old_file != new_image:                            
                            names_id = list_source_2[0][position] 
                            rename_message = self.rename_file_in_nameslink_table(old_file, new_image)                      
                            message += rename_message if rename_message else ""
                    else:
                        message += f"<tr><td>Update ID: {link_satz['NamesID']} {link_satz['Image']} 'Error' </td></tr>"
                if id in update_ids:
                    message += f"<tr><td>Geblieben ID: {link_satz['NamesID']} {link_satz['Image']} </td></tr>"
                    position = list_source_2[0].index(id) 
                    old_file = list_source_2[2][position]
                    rename_message = self.rename_file_in_nameslink_table(old_file)
                    message += rename_message if rename_message else ""
            message += self.delete_old_artist_id(artist_id, datenbank_darsteller)
            MsgBox(self, f"<table border='1'><tr><th>  Performer Link Tabelle  </th></tr>{message}</table>","i")             
        else:
            message += f"{self.delete_artist_id(artist_id, datenbank_darsteller)}" if self.delete_artist_id(artist_id, datenbank_darsteller) else ""
            MsgBox(self, f"<table border='1'><tr><th>  Performer Link Tabelle  </th></tr><tr><td>Keine Einträge in der Performer Link Tabelle</td></tr>{message}</table>","i")
        
    def delete_old_artist_id(self, artist_id: int, datenbank_darsteller) -> str:
        datenbank_darsteller.delete_performer_dataset(artist_id)
        items = self.Main.tblWdg_performer.findItems(str(artist_id), Qt.MatchFlag.MatchExactly)
        row = items[0].row()
        self.Main.tblWdg_performer.removeRow(row)
        return f"<tr><td>alter Datensatz ID: {artist_id} gelöscht </td></tr>"

    def replace_folder(self, image_pfad):
        if image_pfad:            
            artist_images = Path(image_pfad).parents[1]
            new_folder = self.Main.lnEdit_performer_ordner.text()
            filename = Path(image_pfad).name
            image_pfad=str(Path(artist_images, new_folder, filename)).replace("\\","/")
        return image_pfad

    def nameslink_list_to_dict(self, id, link, image, alias):  ### ---- Hilfs Funktionen ---- ###
        return  {"NamesID": id,
                 "Link": link,
                 "Image": image,
                 "Alias": alias  }
    
    def from_dict_to_list(self, names_link_satz):
        names_ids = []
        links = []
        images = []
        aliases = []
        for item in names_link_satz:
            names_ids.append(item['NamesID'])
            links.append(item['Link'])
            images.append(item['Image'])
            aliases.append(item['Alias'])
        return [names_ids, links, images, aliases]

    def rename_file_in_nameslink_table(self, oldfile: str, newfile: str=None) -> str:                
        msg=""
        try:
            if newfile is None:
                raise ValueError("Newfile should not be None.")
            Path(PROJECT_PATH, oldfile).rename(Path(PROJECT_PATH, newfile))
        except (OSError, ValueError, FileExistsError) as os_err:
            if isinstance(os_err, (FileExistsError, ValueError)):
                os_err = "Datei existiert bereits, Datei wurde dann im alten Ordner gelöscht !"                
                Path(PROJECT_PATH, oldfile).unlink()
                msg += f"<tr><td>Gelöscht: {oldfile} , {os_err}</td></tr>"
            elif isinstance(os_err, OSError) and os_err.errno == errno.EACCES:
                os_err = "Die Datei ist noch geöffnet, Zugriff verweigert"
            elif isinstance(os_err, OSError) and os_err.errno == errno.ENOENT:
                os_err = "Datei existiert nicht"
            msg += f"<tr><td>Rename: {oldfile} zu {newfile} mit Error: {os_err}</td></tr>"            
            return msg
        else:
            msg +=self.check_empty_folder(oldfile)
            msg +=f"<tr><td>Rename: {oldfile} zu {newfile} -> erfolgreich</td></tr>" 
            return msg

    def check_empty_folder(self, old_file):
        old_path = PROJECT_PATH / Path(old_file)
        message: str=""
        if old_path.is_dir() and not any(old_path.iterdir()): # altes Verzeichnis löschen, wenn es leer ist                    
            old_path.rmdir()
            message += f"<tr><td>Delete Ordner: /{old_path.name}/</td></tr>"
        else:
            message += f"<tr><td>Ordner: /{old_path.name}/ ist nicht leer</td></tr>"  
        return message           

    def get_studio_id_from_link(self, link, datenbank_darsteller):
        studio_link = f"{urlparse(link).scheme}://{urlparse(link).netloc}/"                       
        studio_id = datenbank_darsteller.get_studio_id_from_baselink(studio_link)
        return studio_id

    def database_to_dict(self, ids, links, images, aliases):
        data_source={}
        if ids:            
            for id, link, image, alias in zip(ids,links,images,aliases):
                data_source |= {id: (link, image, alias)}
        else:
            StatusBar(self.Main,f"Fehler beim Mergen der IDs: {ids}","#FF0000")
        return data_source
    
    def merge_ids_datas(self, data_source_1: dict, data_source_2: dict):
        merged_data = {**data_source_1, **data_source_2}
        list_source = [list(x) for x in zip(*[(key, *value) for key, value in merged_data.items()])] 
        return list_source

    def get_new_and_updated_ids(self, list_source_1, list_source_2):
        ids_1, _, _, _ = list_source_1
        ids_2, _, _, _ = list_source_2
        new_ids = set(ids_2) - set(ids_1)
        updated_ids = set(ids_2) - new_ids
        return list(new_ids), list(updated_ids) 
### ------------------------------------------------------------------------------------ ###
                     
    def showContextMenu_in_Files(self, pos: int) -> None: 
        action_header: QAction = self.set_header_on_contextmenu("Datei Aktionen") 
        menu_dict: dict = {
            "Datei löschen": ("datei_loeschen.png", self.file_delete),
            "Datei umbenennen": ("datei_rename.png", self.file_rename_from_table),
            "Tabelle aktualisieren": ("load_table.png", self.refresh_video_table),
            "abspielen mit VLC": ("vlc.png", self.play_vlc),
            "Datei in dem richtigen Ordner verschieben": ("ordner_verschieben.png", self.file_move_in_db_folder)   }
        self.show_context_menu(pos, action_header, menu_dict)
### ------------------------------------------------------------------------------------ ###
### ------------------------------- Datei Verarbeitung --------------------------------- ###
### ------------------------------------------------------------------------------------ ###
    ### ------------------------------- Datei löschen im ContextMenu ------------------------------ ###
    def file_delete(self):
        self.qdialog_loeschen = uic.loadUi(LOESCH_DIALOG_UI)
        self.qdialog_loeschen.lbl_DELDatei.setText(self.Main.tblWdg_files.selectedItems()[0].text())
        self.qdialog_loeschen.Btn_OK_Abbruch.accepted.connect(self.datei_loeschen)
        self.qdialog_loeschen.Btn_OK_Abbruch.rejected.connect(self.qdialog_loeschen.rejected)
        self.qdialog_loeschen.exec()
    
    def datei_loeschen(self):
        old_file=self.Main.tblWdg_files.selectedItems()[0].text()
        dir=self.Main.lbl_Ordner.text()
        Path(dir,old_file+".mp4").unlink()
        StatusBar(self.Main, f"gelöschte Dateiname: {old_file}","#efffb7")
        zeile=self.Main.tblWdg_files.currentRow()-1
        if zeile>=0:
            self.Main.tblWdg_files.setCurrentCell(zeile, 0)
            self.Main.refresh_table()
        else:
            self.Main.tblWdg_files.clearContents()
            self.Main.tblWdg_files.setRowCount(0)
        self.qdialog_loeschen.hide()

    ### ------------------------------- Datei umbenennen im ContextMenu ------------------------------ ###
    def file_rename_from_table(self):
        self.qdialog_rename = uic.loadUi(RENAME_DIALOG_UI)
        self.qdialog_rename.lnEdit_Rename.setText(self.Main.tblWdg_files.selectedItems()[0].text())
        self.qdialog_rename.Btn_OK_Abbruch.accepted.connect(self.datei_rename)
        self.qdialog_rename.Btn_OK_Abbruch.rejected.connect(self.qdialog_rename.rejected)
        self.qdialog_rename.exec()          
    
    def datei_rename(self):
        old_file=self.Main.tblWdg_files.selectedItems()[0].text()+".mp4"
        new_file=self.qdialog_rename.lnEdit_Rename.text()+".mp4"
        self.Main.lbl_Dateiname.setText(new_file)
        dir=self.Main.lbl_Ordner.text()

        errview=self.Main.file_rename(dir,old_file,new_file)
        if errview=="":
            StatusBar(self, f"Datei in {new_file} umbennant","#efffb7")
            self.Info_Datei_Laden(True)            
            self.Main.tblWdg_files.update()
        self.qdialog_rename.close()
    ### ----------------------------------- refresh video Tabelle ------------------------------------ ###
    def refresh_video_table(self):
        select_file = self.Main.lbl_Dateiname.text()[:-4]
        self.Main.refresh_table(select_file)
    
    ### ----------------------------------- VLC starten im ContextMenu ------------------------------- ### 
    def play_vlc(self):
        directory=self.Main.lbl_Ordner.text()
        filename=self.Main.tblWdg_files.selectedItems()[0].text()+".mp4"
        directory_filename = Path(directory, filename)
        vlc=self.get_vlc_install_path()
        if vlc:
            subprocess.run([vlc+"\\vlc.exe", str(directory_filename)])
    def get_vlc_install_path(self) -> str:
        vlc_path = None
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VideoLAN\VLC")
            vlc_path, _ = winreg.QueryValueEx(key, "InstallDir")
            winreg.CloseKey(key)
        except Exception as e:
            MsgBox(self.Main, f"Fehler beim Ermitteln des VLC-Pfads: {e}","w")
        if vlc_path:
            return vlc_path
        else:
            MsgBox(self.Main, "VLC-Player wurde nicht gefunden.","w")
        
    def file_move_in_db_folder(self):        
        studio: str=""
        directory: str = self.Main.lbl_Ordner.text()
        move_file: str = self.Main.tblWdg_files.selectedItems()[0].text() + ".mp4"
        source_file_path: Path = Path(self.Main.lbl_Ordner.text(), move_file)
        error: str = self.Main.load_exiftool_json(source_file_path)
        if not error and MEDIA_JSON_PATH.exists():
            with open(MEDIA_JSON_PATH,'r') as file:
                file_media_info = json.loads(file.read())[0]
            movies: str=file_media_info.get("Genre","").strip().split("\n")
            studio: str=file_media_info.get("Publisher","")                
        db_webside_settings = Webside_Settings(MainWindow=self.Main) 
        errorview, verschiebe_ordner = db_webside_settings.hole_verschiebe_ordner(studio)        
        if errorview:
            MsgBox(self.Main, f"Datei {move_file} konnte nicht verschoben werden\nDatei-Fehler: '{errorview}'", "w")
            StatusBar(self.Main, f"Fehler: '{errorview}' / Datei {move_file} konnte nicht verschoben werden !", "#efffb7")  # hellgelb)
            return  
        if verschiebe_ordner == directory:
            self.Main.ordner_transfer_zurueck(False,str(Path(verschiebe_ordner,move_file)))
            return        
        target_file_path = Path(verschiebe_ordner) / move_file               
        if target_file_path.exists(): 
            source_size = Path(directory) / move_file
            target_size = target_file_path
            self.Auswahl = uic.loadUi(DATEI_AUSWAHL_UI)
            self.Auswahl.show()
            self.Auswahl.lbl_move_file.setText(move_file)
            self.Auswahl.rdBtn_SourceDatei.setText(f"{directory} <-- ({source_size.stat().st_size / 1024 / 1024:.2f}MB )")
            self.Auswahl.rdBtn_TargetDatei.setText(f"{verschiebe_ordner} <-- ({target_size.stat().st_size / 1024 / 1024:.2f}MB )")
            self.Auswahl.rdBtn_SourceDatei.toggled.connect(lambda: self.Auswahl.rdBtn_TargetDatei.setChecked(not self.Auswahl.rdBtn_SourceDatei.isChecked()))
            self.Auswahl.rdBtn_TargetDatei.toggled.connect(lambda: self.Auswahl.rdBtn_SourceDatei.setChecked(not self.Auswahl.rdBtn_TargetDatei.isChecked()))
            self.Auswahl.btn_OK_radioBtn.clicked.connect(self.Main.auswahl_btn_ok_radiobutton)
        else:
            self.Main.transfer_source(move_file, verschiebe_ordner) 
    ### --------------------------------------------------- ###          
    ### scrape einzeln die daten aus Data18, IAFD und URL's ###
    ### --------------------------------------------------- ### 
    def scrap_synopsis(self, link: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main) 
        
        tool_text = SetTooltipText(self.Main)       
        if link.startswith("https://www.iafd.com/title.rme/"):
            iafd_scene = ScrapeIAFDScene(self.Main)
            check_status.check_loading_labelshow("IAFD") 
            content = iafd_scene.open_url(link, "IAFD") 
            iafd_scene.synopsis_abfrage_iafd(content, link) 
            check_status.check_loaded_labelshow("IAFD")
        elif link.startswith("https://www.data18.com/scenes/"):
            data18_scene = ScrapeData18Scene(self.Main)
            check_status.check_loading_labelshow("Data18")
            content = data18_scene.open_url(link, "Data18") 
            data18_scene.synopsis_abfrage_data18(content, link)
            check_status.check_loaded_labelshow("Data18")
        else:
            check_status.check_loading_labelshow("")
            synopsis: str = None            
            video_updater = VideoUpdater(self.Main)        
            db_website_settings = Webside_Settings(MainWindow=self.Main)
            settings_data = SettingsData()

            message=None
            baselink="/".join(link.split("/")[:3])+"/"
            errview, settings_data = db_website_settings.get_videodatas_from_baselink(baselink)
            if not errview:                
                errview, content, driver = video_updater.open_url_no_javascript(link, settings_data.get_data()["Click"])
                if not errview:
                    synopsis = video_updater.hole_beschreibung_xpath_settings(content, driver, link)
                else: 
                    message=f"beim Scrapen von Videobeschreibung ist dieser Fehler: {errview}"
                if synopsis:
                    DatenbankSceneMaske(self.Main).set_daten_with_tooltip("txtEdit_DB", "Synopsis", baselink, synopsis)
            else:
                message=f"beim Scrapen von Videobeschreibung ist dieser Fehler: {errview}"
                MsgBox(self.Main, message,"w")
            check_status.check_loaded_labelshow("")

    def scrap_movies(self, link: str) -> None: 
        check_status = CheckBioWebsiteStatus(self.Main) 
        
        tool_text = SetTooltipText(self.Main)        
        if link.startswith("https://www.iafd.com/title.rme/"): 
            iafd_scene = ScrapeIAFDScene(MainWindow=self.Main) 
            check_status.check_loading_labelshow("IAFD")       
            content = iafd_scene.open_url(link, "IAFD") 
            iafd_scene.akas_abfrage_iafd(content, link) 
            check_status.check_loaded_labelshow("IAFD")
        if link.startswith("https://www.data18.com/scenes/"):
            data18_scene = ScrapeData18Scene(self.Main)                
            check_status.check_loading_labelshow("Data18")    
            content = iafd_scene.open_url(link, "Data18") 
            iafd_scene.movies_abfrage_data18(content, link)
            check_status.check_loaded_labelshow("Data18")

    def scrap_release(self, link: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)                         
        if link.startswith("https://www.iafd.com/title.rme/"):
            iafd_scene = ScrapeIAFDScene(MainWindow=self.Main)
            check_status.check_loading_labelshow("IAFD")       
            content = iafd_scene.open_url(link, "IAFD") 
            iafd_scene.release_abfrage_iafd(content, link)
            check_status.check_loaded_labelshow("IAFD") 
        if link.startswith("https://www.data18.com/scenes/"):
            data18_scene = ScrapeData18Scene(self.Main)  
            check_status.check_loading_labelshow("Data18")     
            content = data18_scene.open_url(link, "Data18") 
            data18_scene.release_abfrage_data18(content, link)
            check_status.check_loaded_labelshow("Data18")

    def scrap_serie(self, link: str) -> None: 
        check_status = CheckBioWebsiteStatus(self.Main)       
        if link.startswith("https://www.iafd.com/title.rme/"):        
            iafd_scene = ScrapeIAFDScene(MainWindow=self.Main) 
            check_status.check_loading_labelshow("IAFD")       
            content = iafd_scene.open_url(link, "IAFD") 
            iafd_scene.serie_abfrage_iafd(content, link) 
            check_status.check_loaded_labelshow("IAFD")
        if link.startswith("https://www.data18.com/scenes/"):
            data18_scene = ScrapeData18Scene(MainWindow=self.Main)   
            check_status.check_loading_labelshow("Data18")     
            content = data18_scene.open_url(link, "Data18") 
            data18_scene.serie_abfrage_data18(content, link)
            check_status.check_loaded_labelshow("Data18")

    def scrap_regie(self, link: str) -> None:  
        check_status = CheckBioWebsiteStatus(self.Main)      
        if link.startswith("https://www.iafd.com/title.rme/"):        
            iafd_scene = ScrapeIAFDScene(MainWindow=self.Main)  
            check_status.check_loading_labelshow("IAFD")       
            content = iafd_scene.open_url(link, "IAFD") 
            iafd_scene.regie_abfrage_iafd(content, link) 
            check_status.check_loaded_labelshow("IAFD")
        
    def scrap_tags(self, link: str) -> None: 
        check_status = CheckBioWebsiteStatus(self.Main)
        check_status.check_loading_labelshow("")      
        tags: str = None
        baselink = "/".join(link.split("/")[:3])+"/"        
        video_updater = VideoUpdater(baselink, self)        
        db_website_settings = Webside_Settings(MainWindow=self.Main)
        settings_data = SettingsData()        
        errorview, settings_data = db_website_settings.get_videodatas_from_baselink(baselink)
        if not errorview:            
            studio = settings_data.get_data()["Name"]
            errorview, content, driver = video_updater.open_url_javascript(link, "", settings_data.get_data()["Click"])
            errorview, tags = video_updater.hole_tags_xpath_settings(content, link, driver, self.Main)
            if tags:
                DatenbankSceneMaske(self.Main).set_daten_with_tooltip("txtEdit_DB", "Tags", baselink, tags)
            else: 
                self.Main.txtEdit_Clipboard.setText(f"Fehler bei Tags: {errorview}")    
        else:
            MsgBox(self.Main, f"beim scrape von Tags ist dieser Fehler: {errorview}","w")
        check_status.check_loaded_labelshow("")

    def scrap_scenecode(self, link: str) -> None:
        pass

    def scrap_prodate(self, link: str) -> None:
        pass

