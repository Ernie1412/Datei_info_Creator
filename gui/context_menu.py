from PyQt6 import uic
from PyQt6.QtWidgets import QMenu, QTableWidgetItem 
from PyQt6.QtGui import QAction, QCursor

import functools
import json
import winreg
import subprocess
from pathlib import Path

from utils.database_settings.database_for_settings import Webside_Settings, SettingsData
from utils.web_scapings.websides import Infos_WebSides
from utils.web_scapings.scrap_with_requests import VideoUpdater
from utils.database_settings.database_for_darsteller import DB_Darsteller
from utils.web_scapings.load_performer_images_from_websites import LoadAnalVidsPerformerImages

from gui.dialoge_ui.message_show import MsgBox, StatusBar

from config import MEDIA_JSON_PATH
from config import LOESCH_DIALOG_UI, RENAME_DIALOG_UI, DATEI_AUSWAHL_UI, PROJECT_PATH


class ContextMenu(QMenu):
    def __init__(self, parent = None ):
        super().__init__()
        self.Main = parent

    ### --------------------------------------------------------------------- ###
    ### ------Pushup Menu inder Tabelle ------------------------------------- ###
    ### --------------------------------------------------------------------- ###
    def showContextMenu(self, pos: int, widget_name) -> None:
        current_widget = self.sender()        
        if current_widget:            
            # Hier je nach widget_name die entsprechende Aktion ausführen
            if current_widget == self.Main.tblWdg_Files:
                self.showContextMenu_in_Files(current_widget.mapToGlobal(pos))
            elif current_widget == self.Main.txtEdit_DBSynopsis:
                self.showContextMenu_in_Synopsis(current_widget.mapToGlobal(pos))
            elif current_widget == self.Main.txtEdit_DBTags:
                self.showContextMenu_in_DBTags(current_widget.mapToGlobal(pos))
            elif current_widget == self.Main.tblWdg_performer_links:
                self.showContextMenu_in_performer_links(current_widget.mapToGlobal(pos))

    def showContextMenu_in_Files(self, pos: int) -> None: 
        action_header: QAction = self.set_header_on_contextmenu("Datei Aktionen") 
        menu_dict: dict = {
            "Datei löschen": self.file_delete,
            "Datei umbenennen": self.file_rename_from_table,
            "Tabelle aktualisieren": self.Main.refresh_table,
            "abspielen mit VLC": self.play_vlc,
            "Datei in dem richtigen Ordner verschieben": self.file_move_in_db_folder   }
        self.show_context_menu(pos, action_header, menu_dict) 

    #### ----------- Aufruf für die 'Performer Links Tabelle' ----------- #####
    def showContextMenu_in_performer_links(self, pos: int) -> None: # tblWdg_performer_links
        action_header: QAction = self.set_header_on_contextmenu("Tabelle Performer Links") 
        menu_dict: dict = {
            "Zeile hinzufügen": self.add_item,
            "Zeile löschen": self.delete_item,
            "lade Tabelle neu aus Datenbank": self.refresh_tabelle,
            "Lade Bild von Website": self.load_image_from_webside,
            "Tabellespalten am Text anpassen": self.context_resize,
            "Explorer im Namen Ordner öffnen": self.open_explorer     }
        self.show_context_menu(pos, action_header, menu_dict)

    #### ----------- Aktionen in dem 'Performer Links Tabelle' ----------- #####
    def add_item(self):
        pass

    def delete_item(self):
        name=self.Main.lnEdit_performer_info.text()
        if self.Main.tblWdg_performer_links.rowCount()>-1 and name:        
            row_index = self.Main.tblWdg_performer_links.currentRow()
            if row_index >= 0:
                datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
                names_id=self.Main.tblWdg_performer_links.selectedItems()[0].text()
                errview = datenbank_darsteller.delete_nameslink_satz(names_id) 
                self.Main.tblWdg_performer_links.removeRow(row_index)
                self.Main.lbl_db_status.setText(f"Zeile: {row_index+1} mit der ID: {names_id} wurde auch aus der Datenbank gelöscht !")
        else:
            self.Main.lbl_db_status.setText("Kein Name oder nichts in der Tabelle drin !") 

    def refresh_tabelle(self):
        name=self.Main.lnEdit_performer_info.text()
        if self.Main.tblWdg_performer_links.rowCount()>-1 and name:
            datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
            errview, ids, links, images, aliases = datenbank_darsteller.get_quell_links(self.Main.tblWdg_Daten.selectedItems()[0].text()) #ArtistID -> DB_NamesLink.NamesID
            for zeile,(id, link, image, alias) in enumerate(zip(ids,links,images,aliases)):
                self.Main.tblWdg_performer_links.setRowCount(zeile+1)
                self.Main.tblWdg_performer_links.setItem(zeile,0,QTableWidgetItem(f"{id}"))            
                self.Main.tblWdg_performer_links.setItem(zeile,1,QTableWidgetItem(link))
                self.Main.tblWdg_performer_links.setItem(zeile,2,QTableWidgetItem(image))
                self.Main.tblWdg_performer_links.setItem(zeile,3,QTableWidgetItem(alias))
            self.Main.tblWdg_performer_links.resizeColumnsToContents()
        else:
            self.Main.lbl_db_status.setText("Kein Name oder nichts in der Tabelle drin !") 

    def load_image_from_webside(self):
        name=self.Main.lnEdit_performer_info.text()
        if self.Main.tblWdg_performer_links.rowCount()>-1 and name:
            load = LoadAnalVidsPerformerImages(MainWindow=self.Main, name=name)
            load.load_analvids_image_in_label()
        else:
            self.Main.lbl_db_status.setText("Kein Name oder nichts in der Tabelle drin !")            

    def context_resize(self):
        self.Main.tblWdg_performer_links.resizeColumnsToContents()
        self.Main.tblWdg_performer_links.update()

    def open_explorer(self):
        name=self.Main.lnEdit_performer_info.text()
        subprocess.Popen(['explorer', str(PROJECT_PATH / f"__artists_Images/{name}")])

    #### -------------------------------------------------------------------------- #####

    def showContextMenu_in_DBSceneCode(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Scene Code !")       
        menu_dict = self.action_links(self.scrap_scenecode)
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_DBTags(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Scene Code !")       
        menu_dict = self.action_links(self.scrap_tags)
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_DBProDate(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Productions Datum !")       
        menu_dict = self.action_links(self.scrap_prodate)
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_Synopsis(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Synopsis !")       
        menu_dict = self.action_links(self.scrap_synopsis)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = functools.partial(self.scrap_synopsis, self.Main.lnEdit_DBData18Link.text())
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = functools.partial(self.scrap_synopsis,self.Main.lnEdit_DBIAFDLink.text())

        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_regie(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Regieseur !")       
        menu_dict = self.action_links(self.scrap_regie)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = functools.partial(self.scrap_regie, self.Main.lnEdit_DBData18Link.text())
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = functools.partial(self.scrap_regie,self.Main.lnEdit_DBIAFDLink.text())
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_serie(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Serie/Unter-Studio !")       
        menu_dict = self.action_links(self.scrap_serie)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = functools.partial(self.scrap_serie, self.Main.lnEdit_DBData18Link.text())
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = functools.partial(self.scrap_serie,self.Main.lnEdit_DBIAFDLink.text())
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_release(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Release Datum !")       
        menu_dict = self.action_links(self.scrap_release)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = functools.partial(self.scrap_release, self.Main.lnEdit_DBData18Link.text())
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = functools.partial(self.scrap_release,self.Main.lnEdit_DBIAFDLink.text())
        self.show_context_menu(pos, action_header, menu_dict)

    def showContextMenu_in_movies(self, pos: int) -> None:
        action_header: QAction = self.set_header_on_contextmenu("Webscrapen von Movies und Alias !")       
        menu_dict = self.action_links(self.scrap_movies)
        if self.Main.lnEdit_DBData18Link:
            menu_dict["Data18"] = functools.partial(self.scrap_movies, self.Main.lnEdit_DBData18Link.text())
        if self.Main.lnEdit_DBIAFDLink:            
            menu_dict["IAFD"] = functools.partial(self.scrap_movies,self.Main.lnEdit_DBIAFDLink.text())
        self.show_context_menu(pos, action_header, menu_dict)

    def show_context_menu(self, pos: int, action_header: QAction, menu_dict: dict) -> None:
        context_menu = QMenu(self.Main)
        
        context_menu.addAction(action_header)                          
        for menu, func in menu_dict.items():
            action = QAction(menu, self.Main)            
            action.triggered.connect(func)
            context_menu.addAction(action) 
        context_menu.setStyleSheet("QMenu::item:disabled {background: transparent;}")
        context_menu.exec(QCursor.pos())

    def set_header_on_contextmenu(self, header: str) -> QAction:
        action_readonly = QAction(header, self)
        font = action_readonly.font()
        font.setBold(True)       
        action_readonly.setFont(font)        
        action_readonly.setEnabled(False)          
        
        return action_readonly 

    def action_links(self, scraper_function) -> dict:        
        menu_dict = {}        
        for index in range(self.Main.model_database_weblinks.rowCount()):
            links = self.Main.model_database_weblinks.data(self.Main.model_database_weblinks.index(index, 0))
            web_link = links.split("/")[2]
            menu_dict[web_link] = functools.partial(scraper_function, links)            
        return menu_dict

    ### --------------------------------------------------------------------- ###
    ### ------Pushup Menu reagiert nun auf if Anweisungen-------------------- ###
    ### --------------------------------------------------------------------- ###

    ### ------------------------------- Datei löschen im ContextMenu --------------------------------- ###
    def file_delete(self):
        self.DIA_Loeschen = uic.loadUi(LOESCH_DIALOG_UI)
        self.DIA_Loeschen.lbl_DELDatei.setText(self.Main.tblWdg_Files.selectedItems()[0].text())
        self.DIA_Loeschen.Btn_OK_Abbruch.accepted.connect(self.Main.Datei_loeschen)
        self.DIA_Loeschen.Btn_OK_Abbruch.rejected.connect(self.DIA_Loeschen.rejected)
        self.DIA_Loeschen.exec()

    ### ------------------------------- Datei umbenennen im ContextMenu ------------------------------ ###
    def file_rename_from_table(self):
        self.DIA_Rename = uic.loadUi(RENAME_DIALOG_UI)
        self.DIA_Rename.lnEdit_Rename.setText(self.Main.tblWdg_Files.selectedItems()[0].text())
        self.DIA_Rename.Btn_OK_Abbruch.accepted.connect(self.Main.Datei_Rename)
        self.DIA_Rename.Btn_OK_Abbruch.rejected.connect(self.DIA_Rename.rejected)
        self.DIA_Rename.exec()
        self.Main.tblWdg_Files.update()
  
    
    ### ----------------------------------- VLC starten im ContextMenu ------------------------------- ### 
    def play_vlc(self):
        directory=self.Main.lbl_Ordner.text()
        filename=self.Main.tblWdg_Files.selectedItems()[0].text()+".mp4"
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
        # Ermitteln Sie die erforderlichen Informationen
        studio: str=""
        directory: str = self.Main.lbl_Ordner.text()
        move_file: str = self.Main.tblWdg_Files.selectedItems()[0].text() + ".mp4"
        source_file_path: Path = Path(self.Main.lbl_Ordner.text(), move_file)
        error: str = self.Main.load_exiftool_json(source_file_path)
        if not error and MEDIA_JSON_PATH.exists():
            with open(MEDIA_JSON_PATH,'r') as file:
                file_media_info = json.loads(file.read())[0]
            movies: str=file_media_info.get("Genre","").strip().split("\n")
            studio: str=file_media_info.get("Publisher","")                
        db_webside_settings = Webside_Settings(MainWindow=self.Main) 
        errorview, verschiebe_ordner = db_webside_settings.hole_verschiebe_ordner(studio)

        # Überprüfen Sie, ob ein Fehler aufgetreten ist
        if errorview:
            MsgBox(self.Main, f"Datei {move_file} konnte nicht verschoben werden\nDatei-Fehler: '{errorview}'", "w")
            StatusBar(self.Main, f"Fehler: '{errorview}' / Datei {move_file} konnte nicht verschoben werden !", "#efffb7")  # hellgelb)
            return
        
        # Überprüfen Sie, ob das Verschieben erforderlich ist
              
        if verschiebe_ordner == directory:
            self.Main.ordner_transfer_zurueck(False,str(Path(verschiebe_ordner,move_file)))
            return

        # Überprüfen Sie, ob die Datei im Zielordner vorhanden ist 
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
        websides = Infos_WebSides(MainWindow=self.Main)       
        if link.startswith("https://www.iafd.com/title.rme/"):
            websides.check_loading_labelshow("IAFD") 
            content = websides.open_url(link, "IAFD") 
            websides.synopsis_abfrage_iafd(content, link) 
            self.check_loaded_labelshow("IAFD")
        elif link.startswith("https://www.data18.com/scenes/"):
            websides.check_loading_labelshow("Data18")
            content = websides.open_url(link, "Data18") 
            websides.synopsis_abfrage_data18(content, link)
            self.check_loaded_labelshow("Data18")
        else:
            websides.check_loading_labelshow("")
            synopsis: str = None            
            video_updater = VideoUpdater(self)        
            db_website_settings = Webside_Settings(MainWindow=self.Main)
            settings_data = SettingsData()

            baselink="/".join(link.split("/")[:3])+"/"
            errorview, settings_data = db_website_settings.get_videodatas_from_baselink(baselink)
            if not errorview:            
                studio=settings_data.get_data()["Name"]
                errorview, content, driver = video_updater.open_url_webside(link, settings_data.get_data()["Click"])
                synopsis = video_updater.hole_beschreibung_xpath_settings(errorview, content, driver)
                if synopsis:
                    websides.set_daten_with_tooltip("txtEdit_DB", "Synopsis", baselink, synopsis)
            else:
                MsgBox(self.Main, f"beim scrape von Videobeschreibung ist dieser Fehler: {errorview}","w")
            websides.check_loaded_labelshow("")

    def scrap_movies(self, link: str) -> None:        
        if link.startswith("https://www.iafd.com/title.rme/"):        
            websides = Infos_WebSides(MainWindow=self.Main) 
            websides.check_loading_labelshow("IAFD")       
            content = websides.open_url(link, "IAFD") 
            websides.akas_abfrage_iafd(content, link) 
            websides.check_loaded_labelshow("IAFD")
        if link.startswith("https://www.data18.com/scenes/"):
            websides = Infos_WebSides(MainWindow=self.Main)    
            websides.check_loading_labelshow("Data18")    
            content = websides.open_url(link, "Data18") 
            websides.movies_abfrage_data18(content, link)
            websides.check_loaded_labelshow("Data18")

    def scrap_release(self, link: str) -> None:        
        if link.startswith("https://www.iafd.com/title.rme/"):        
            websides = Infos_WebSides(MainWindow=self.Main) 
            websides.check_loading_labelshow("IAFD")       
            content = websides.open_url(link, "IAFD") 
            websides.release_abfrage_iafd(content, link)
            websides.check_loaded_labelshow("IAFD") 
        if link.startswith("https://www.data18.com/scenes/"):
            websides = Infos_WebSides(MainWindow=self.Main)  
            websides.check_loading_labelshow("Data18")     
            content = websides.open_url(link, "Data18") 
            websides.release_abfrage_data18(content, link)
            websides.check_loaded_labelshow("Data18")

    def scrap_serie(self, link: str) -> None:        
        if link.startswith("https://www.iafd.com/title.rme/"):        
            websides = Infos_WebSides(MainWindow=self.Main) 
            websides.check_loading_labelshow("IAFD")       
            content = websides.open_url(link, "IAFD") 
            websides.serie_abfrage_iafd(content, link) 
            websides.check_loaded_labelshow("IAFD")
        if link.startswith("https://www.data18.com/scenes/"):
            websides = Infos_WebSides(MainWindow=self.Main)   
            websides.check_loading_labelshow("Data18")     
            content = websides.open_url(link, "Data18") 
            websides.serie_abfrage_data18(content, link)
            websides.check_loaded_labelshow("Data18")

    def scrap_regie(self, link: str) -> None:        
        if link.startswith("https://www.iafd.com/title.rme/"):        
            websides = Infos_WebSides(MainWindow=self.Main) 
            websides.check_loading_labelshow("IAFD")       
            content = websides.open_url(link, "IAFD") 
            websides.regie_abfrage_iafd(content, link) 
            websides.check_loaded_labelshow("IAFD")

        
    def scrap_tags(self, link: str) -> None: 
        websides = Infos_WebSides(MainWindow=self.Main) 
        websides.check_loading_labelshow("")      
        tags: str = None
        baselink = "/".join(link.split("/")[:3])+"/"        
        video_updater = VideoUpdater(baselink, self)        
        db_website_settings = Webside_Settings(MainWindow=self.Main)
        settings_data = SettingsData()
        
        errorview, settings_data = db_website_settings.get_videodatas_from_baselink(baselink)
        if not errorview:            
            studio=settings_data.get_data()["Name"]
            errorview, content, driver = video_updater.open_url_javascript(link, settings_data.get_data()["Click"])
            tags = video_updater.hole_tags_xpath_settings(content, driver, link)
            if tags:
                websides.set_daten_with_tooltip("txtEdit_DB", "Tags", baselink, tags)
        else:
            MsgBox(self.Main, f"beim scrape von Tags ist dieser Fehler: {errorview}","w")
        websides.check_loaded_labelshow("")

    def scrap_scenecode(self, link: str) -> None:
        pass

    def scrap_prodate(self, link: str) -> None:
        pass

