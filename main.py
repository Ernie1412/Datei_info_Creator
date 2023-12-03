from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTranslator, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QAbstractItemView, QTableWidgetItem, QApplication, QPushButton, QWidget, QListWidgetItem , \
    QListWidget, QLineEdit, QTextEdit, QComboBox
from PyQt6.QtGui import QMovie, QPixmap, QKeyEvent, QStandardItem, QStandardItemModel, QColor, QBrush

import sys
import json
import subprocess
import re
from datetime import datetime
import pyperclip
import win32com.client
from pathlib import Path
from typing import List, Tuple
from scrapy.settings import Settings

import gui.resource_collection_files.logo_rc
import gui.resource_collection_files.buttons_rc

from utils.database_settings import DB_Darsteller, Webside_Settings, ScrapingData, VideoData
from utils.web_scapings.websides import Infos_WebSides
from utils.web_scapings.iafd_performer_link import IAFDInfos
from utils.web_scapings.performer_infos_maske import PerformerInfosMaske
from utils.threads import FileTransferThread, ExifSaveThread
from utils.umwandeln import from_classname_to_import, count_days
from gui.dialoge_ui.message_show import StatusBar, MsgBox, status_fehler_ausgabe
from gui.dialoge_ui.einstellungen import Einstellungen
from gui.dialoge_ui.dialog_daten_auswahl import Dlg_Daten_Auswahl
from gui.context_menu import ContextMenu
from gui.show_performer_images import ShowPerformerImages

from config import EXIFTOOLPFAD
from config import BUTTONSNAMES_JSON_PATH, PROCESS_JSON_PATH, MEDIA_JSON_PATH, DATENBANK_JSON_PATH
from config import MAIN_UI, BUTTONS_WEBSIDES_UI, TRANSFER_UI
          
### -------------------------------------------------------------------- ###
### --------------------- HauptFenster --------------------------------- ###
### -------------------------------------------------------------------- ###
class Haupt_Fenster(QMainWindow):    
    def __init__(self, parent=None):
        super(Haupt_Fenster,self).__init__(parent)        
        uic.loadUi(MAIN_UI,self)
        self.showMaximized() 

        self.buttons_connections()        

        if Path(DATENBANK_JSON_PATH).exists():            
            Path(DATENBANK_JSON_PATH).unlink()          
        self.model_database_weblinks = QStandardItemModel()
        self.lstView_database_weblinks.setModel(self.model_database_weblinks) 
        

        #### -----------  setze Sichtbarkeit auf "False" ----------- #####         
        self.invisible_lbl_anzahl()
        self.invisible_any_labels() 


    def buttons_connections(self): 
        self.show_performers_images = ShowPerformerImages(self)                    
    ###-------------------------auf Klicks reagieren--------------------------------------###        
        self.Btn_Laden.clicked.connect(self.Infos_ExifToolHolen)
        self.Btn_Speichern.clicked.connect(self.Infos_Speichern)
        self.Btn_Refresh.clicked.connect(self.refresh_table)
        self.Btn_Loeschen.clicked.connect(self.tabs_clearing)  
        self.Btn_VideoDatenHolen.clicked.connect(self.videodaten_holen)        
        self.Btn_Rechts.clicked.connect(self.AddRechts)
        self.Btn_Links.clicked.connect(self.AddLinks)
        ### --- Buttons auf den Infos Tab ------ #####
        self.Btn_logo_am_infos_tab.clicked.connect(self.Websides_Auswahl)
        self.Btn_AddArtist.clicked.connect(self.AddArtist)
        self.Btn_Linksuche_in_DB.clicked.connect(self.linksuche_in_db)        
        ### ------------------------------------- ####
        ### --- Buttons auf den Analyse Tab ---- #####
        self.Btn_logo_am_analyse_tab.clicked.connect(self.Websides_Auswahl)
        self.Btn_titel_suche.clicked.connect(self.titel_suche)
        self.Btn_name_suche.clicked.connect(self.performer_suche)
        self.cBox_performers.currentIndexChanged.connect(self.show_performers_images.show_performer_picture)
        self.Btn_next.clicked.connect(self.show_performers_images.show_next_picture_in_label)
        self.Btn_prev.clicked.connect(self.show_performers_images.show_previous_picture_in_label)
        ### ------------------------------------- ####
        ### --- Buttons auf den Datenbank Tab ---- ##### 
        self.Btn_logo_am_db_tab.clicked.connect(self.Websides_Auswahl)
        self.Btn_Linksuche_in_URL.clicked.connect(self.webscrap_url)
        self.Btn_Linksuche_in_Data18.clicked.connect(self.webscrap_data18)
        self.Btn_Linksuche_in_IAFD.clicked.connect(self.webscrap_iafd)
        self.Btn_AddLink.clicked.connect(self.addLink)
        self.Btn_delLink.clicked.connect(self.delete_link_from_listview)
        self.Btn_AddPerformer.clicked.connect(self.add_performers)
        self.Btn_delPerformer.clicked.connect(self.del_performers)          
        self.Btn_Clipboard.clicked.connect(self.CopyText)
        self.Btn_DBUpdate.clicked.connect(self.single_DBupdate)
        self.Btn_addDatei.clicked.connect(self.add_db_in_datei)       

        felder = ["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Movies", "Synopsis", "Tags"]                                          
        for feld in felder:            
            button_widget = self.findChild(QPushButton, f'Btn_Anzahl_DB{feld}')
            Line_edit_widget = self.findChild(QLineEdit, f'lnEdit_DB{feld}')
            text_edit_widget = self.findChild(QTextEdit, f'txtEdit_DB{feld}')
            if button_widget:
                button_widget.clicked.connect(self.dialog_auswahl)
            if Line_edit_widget or text_edit_widget:
                widget_obj = Line_edit_widget or text_edit_widget  
                widget_obj.customContextMenuRequested.connect(lambda pos, widget_obj=widget_obj: self.showContextMenu(pos, widget_obj))

        ### ----------------------------------------- #####
        self.Btn_IAFD_linkmaker.clicked.connect(self.link_maker)
        self.Btn_DateiLaden.clicked.connect(self.Info_Datei_Laden)
        self.Btn_get_last_side.clicked.connect(self.gui_last_side) 
        self.Btn_start_spider.clicked.connect(self.start_spider)  
        self.Btn_RadioBtn_rename.clicked.connect(self.file_rename_from_infos) 
        self.Btn_Titelsuche_in_DB.clicked.connect(self.titel_suche)
        self.Btn_perfomsuche_in_DB.clicked.connect(self.performer_suche)          
        self.rdBtn_rename.clicked.connect(self.radioBtn_file_rename)         
        self.actionEinstellungen.triggered.connect(self.einstellungen_ui_show)
        self.tblWdg_Daten.horizontalHeader().sectionClicked.connect(lambda index: self.tblWdg_Daten.setSortingEnabled(not self.tblWdg_Daten.isSortingEnabled()))
        self.tblWdg_Daten.clicked.connect(self.DB_Anzeige)
        self.tblWdg_Files.clicked.connect(self.Ordner_Infos)        
        self.tblWdg_Files.horizontalHeader().sectionClicked.connect(lambda index: self.tblWdg_Files.setSortingEnabled(not self.tblWdg_Files.isSortingEnabled()))        
        self.tblWdg_Files.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  
        ### --- Context Menus ---------------------- ### 
        self.tblWdg_Files.customContextMenuRequested.connect(lambda pos, widget_obj=self.tblWdg_Files: self.showContextMenu(pos, widget_obj))
        ### ------------ Text/Tab Wechsel Reaktion ------------------ ###
        self.lnEdit_URL.textChanged.connect(lambda index: self.Btn_Linksuche_in_DB.setEnabled(bool(self.lnEdit_URL.text().startswith("https://"))))
        self.tabs.currentChanged.connect(self.tab_changed_handler)
        self.lnEdit_DBIAFDLink.textChanged.connect(self.Web_IAFD_change)
        self.lnEdit_DBData18Link.textChanged.connect(self.Web_Data18_change)              
        self.lnEdit_URL.textChanged.connect(self.link_isin_from_db)
        self.lnEdit_db_titel.textChanged.connect(self.titelsuche_in_DB_aktiv)
        self.lnEdit_db_performer.textChanged.connect(self.performersuche_in_DB_aktiv)
        self.cBox_studio_links.currentIndexChanged.connect(lambda index :self.Btn_start_spider.setEnabled(bool(self.cBox_studio_links.currentText()))) 
        ### ---------------- Performer Tab --------------------------- ###
        self.lnEdit_DBIAFD_artistLink.textChanged.connect(self.Web_IAFD_artist_change)
        self.lnEdit_DBBabePedia_artistLink.textChanged.connect(self.Web_BabePedia_artist_change) 
        self.Btn_IAFD_perfomer_suche.clicked.connect(self.get_IAFD_performer_link) 
        self.Btn_Linksuche_in_IAFD_artist.clicked.connect(self.load_IAFD_performer_link) 
        self.cBox_performer_sex.currentIndexChanged.connect(self.set_iafd_button_and_tooltip)
        self.Btn_DB_perfomer_suche.clicked.connect(self.datenbank_performer_suche)        
        self.Btn_DBArtist_Update.clicked.connect(self.update_datensatz)
        self.Btn_table_links_expanding.clicked.connect(self.expand_table_links)
        self.Btn_table_daten_expanding.clicked.connect(self.expand_table_daten)
        self.Btn_seiten_vor.clicked.connect(self.datenbank_performer_suche_nextpage)
        self.Btn_seiten_zurueck.clicked.connect(self.datenbank_performer_suche_prevpage)
        self.tblWdg_performer_links.clicked.connect(self.show_performers_images.show_performer_picture)
        self.Btn_performer_next.clicked.connect(self.show_performers_images.show_next_picture_in_label)
        self.Btn_performer_prev.clicked.connect(self.show_performers_images.show_previous_picture_in_label)
        ###-----------------------------------------------------------------------------------###
        for i in range(1,6):            
            stacked_widget = self.findChild(QPushButton, f'Btn_stacked_next_{i}')  
            stacked_widget.clicked.connect(lambda: self.stackedWidget.setCurrentIndex((self.stackedWidget.currentIndex() + 1) % self.stackedWidget.count()))

    def tab_changed_handler(self, index: int) -> None:
        if index > 0:
            self.tblWdg_Daten.raise_()
        else:
            self.tblWdg_Files.raise_()

        if index == 0:
            self.stackedWidget.setCurrentIndex(0)

        if index == 1: 
            self.stackedWidget.setCurrentWidget(self.stacked_db_abfrage)           
            self.set_analyse_daten()

        if index ==2: 
            self.stackedWidget.setCurrentWidget(self.stacked_IAFD_Linkmaker) 
            header_labels=["Titel", "WebLinks", "IAFDLink", "Performer", "Action", "Name", "Dauer","Release Date", "Productions Date"
                "Serie","Regie","Scene Code","Movies","Synopsis","Tags"]
            self.tblWdg_Daten.setColumnCount(len(header_labels))
            self.tblWdg_Daten.setHorizontalHeaderLabels(header_labels)          
            links = self.lstView_database_weblinks.model().data(self.lstView_database_weblinks.model().index(0, 0))
            if links:
                self.set_studio_in_db_tab(links)

        if index ==3:
            self.stackedWidget.setCurrentWidget(self.stacked_IAFD_artist)
            header_labels=["ID", "Name", "IAFD", "BabePedia", "Geschlecht", "Rasse", "Nation", "Geburtstag", "Geburtsort",  "OnylFans", "Boobs","Gewicht",
                "Größe","Bodytyp", "Piercing","Tattoo","Haarfarbe", "Augenfarbe","Aktiv"]            
            self.tblWdg_Daten.setColumnCount(len(header_labels))
            self.tblWdg_Daten.setHorizontalHeaderLabels(header_labels)


    def set_studio_in_db_tab(self, links):
        scraping_data = ScrapingData(MainWindow=self)
        studio_name = scraping_data.from_link_to_studio(links.split("/")[2])
        db_webside_settings = Webside_Settings(MainWindow=self)
        errorview, studio, logo = db_webside_settings.get_buttonlogo_from_studio(studio_name)  
        if errorview:
            logo="background-image: url(':/Buttons/grafics/no-logo_90x40.jpg')"
            studio="kein Studio ausgewählt !"
        self.Btn_logo_am_db_tab.setStyleSheet(logo)
        self.Btn_logo_am_db_tab.setToolTip(studio)

    def showContextMenu(self, pos: int, widget_name):        
        current_widget = self.sender()
        if current_widget:
            context_menu = ContextMenu(self)
            context_menu.showContextMenu(current_widget.mapToGlobal(pos), widget_name)
    
    def refresh_table(self, new_file: str=None) -> None: 
        sort = self.tblWdg_Files.isSortingEnabled()
        gesuchter_text = new_file if new_file else self.tblWdg_Files.selectedItems()[0].text() # wenn es vom rename func kommt, new_file            
        self.tblWdg_Files.hide()
        self.Info_Datei_Laden(refresh=True)
        QTimer.singleShot(300, lambda :self.tblWdg_Files.show())
        self.tblWdg_Files.setSortingEnabled(sort)
        for row in range(self.tblWdg_Files.rowCount()):
            item = self.tblWdg_Files.item(row, 0)  # Hier 0 für die erste Spalte, ändere es entsprechend
            if item and item.text() == gesuchter_text:
                item.setSelected(True)
                # Du hast die gewünschte Zeile gefunden (row)
                break

        
        

    def titelsuche_in_DB_aktiv(self):
        if self.Btn_logo_am_db_tab.toolTip() != "kein Studio ausgewählt !":            
            self.Btn_Titelsuche_in_DB.setEnabled(True)

    def performersuche_in_DB_aktiv(self):
        if self.Btn_logo_am_db_tab.toolTip() != "kein Studio ausgewählt !":
            self.Btn_perfomsuche_in_DB.setEnabled(True)

    #### ----- einiges Labels erstmal unsichtbar setzen ----- ####
    ##############################################################
    def invisible_lbl_anzahl(self):
        lbl_anzahl_db: list = ["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Movies", "Synopsis", "Tags"]        
        for anzahl in lbl_anzahl_db:
            getattr(self, f"Btn_Anzahl_DB{anzahl}").setVisible(False)
    
    def invisible_any_labels(self):
        labels: list = ["SceneCode", "ProDate", "Regie", "_checkWeb_Data18URL", "_checkWeb_URL", "_checkWeb_IAFDURL"]
        line_edits: list = ["ProDate","Regie"]
        for label in labels:
            getattr(self, f"lbl{label}").setVisible(False)
        for line_edit in line_edits:
            getattr(self, f"lnEdit_{line_edit}").setVisible(False)
    ##############################################################
        
    def loesche_DB_maske(self):
        line_edit_dbs=["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Data18Link", "IAFDLink"]        
        text_edit_dbs=["Movies", "Tags", "Synopsis"] 

        for line_edit_db in line_edit_dbs:
            getattr(self, f"lnEdit_DB{line_edit_db}").clear()
               
        for text_edit_db in text_edit_dbs:
            getattr(self, f"txtEdit_DB{text_edit_db}").clear()

        
    ### --------------------------------------------------------------------- ###
    def radioBtn_file_rename(self):
        if self.tblWdg_Files.rowCount() == 0 or self.lnEdit_Studio.text() == "":
            zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
            StatusBar(self, f"{zeit}: Die Tabelle oder das PornSide Label ist leer ! Umbennen nicht möglich !","#ffc1d2")            
            self.rdBtn_rename.setChecked(False) 
            self.Btn_RadioBtn_rename.setEnabled(False)           
        else:
            self.Btn_RadioBtn_rename.setEnabled(not self.Btn_RadioBtn_rename.isEnabled())

        
    def datenbank_save(self,info_art: str, source: str=None, daten: str=None) -> None:
        if info_art == "delete":
        # Lösche die JSON-Datei und beende die Funktion
            if Path(DATENBANK_JSON_PATH).exists():
                Path(DATENBANK_JSON_PATH).unlink()
                self.invisible_lbl_anzahl()
                self.loesche_DB_maske()
            return

        if Path(DATENBANK_JSON_PATH).exists():
            set = json.loads(DATENBANK_JSON_PATH.read_bytes())
        else:
            set = {} 

        if info_art in set and source in set[info_art] and set[info_art][source] == daten:
            # Die Daten sind bereits vorhanden, daher nicht erneut speichern
            return
        
        if info_art not in set:
            set[info_art] = {}
        if daten in set[info_art].values():
        # Die Daten sind bereits vorhanden, daher nicht erneut speichern
            return
        # Füge die Informationen aus der übergebenen Quelle hinzu

        set[info_art][source] = daten
        anzahl=len(set[info_art])
        if anzahl > 1:
            getattr(self, f"Btn_Anzahl_DB{info_art}").setText(f"{anzahl}")
            getattr(self, f"Btn_Anzahl_DB{info_art}").setVisible(True)
        
        json.dump(set,open(DATENBANK_JSON_PATH,'w'),indent=4, sort_keys=True) 
    ### --------------------------------------------------------------------- ###
    ### ------ lade daten aus einem Zwischenspeicher(json) ------------------ ###
    ### --------------------------------------------------------------------- ###
    def datenbank_load_maske(self, info_art: str) -> Tuple[List[str], List[str]]:
        if Path(DATENBANK_JSON_PATH).exists():            
            set = json.loads(DATENBANK_JSON_PATH.read_bytes())
            return set[info_art].keys(),set[info_art].values()
        return [], []
    

    def auswahl_btn_ok_radiobutton(self):
        self.Auswahl.reject()
        db_webside_settings = Webside_Settings(MainWindow=self)
        errorview,verschiebe_ordner = db_webside_settings.hole_verschiebe_ordner(self.lbl_SuchStudio.text())
        move_file = self.tblWdg_Files.selectedItems()[0].text()+".mp4" 
        if self.Auswahl.rdBtn_TargetDatei.isChecked():            
            Path(self.lbl_Ordner.text(), move_file).unlink()             
            self.Auswahl.hide() 
            self.refresh_table()                     
            StatusBar(self, f"Datei {move_file} wird in {verschiebe_ordner} bevorzugt, andere Datei wurde gelöscht !","#efffb7")#hellgelb) 
        else:                        
            self.transfer_source(move_file,verschiebe_ordner) 

    def transfer_source(self,move_file: str ,verschiebe_ordner: str) -> None:
        # Zeigen Sie die Informationen im Transfer-Fenster an
        directory: str=self.lbl_Ordner.text()
        self.Transfer = uic.loadUi(TRANSFER_UI)        
        self.Transfer.lbl_move_file.setText(move_file)
        self.Transfer.lbl_Source_Folder.setText(directory)
        self.Transfer.lbl_Dest_Folder.setText(verschiebe_ordner)
        self.Transfer.prgBar_Transfer.setValue(0)
        self.Transfer.show()  
        self.Transfer.setWindowTitle("Datei Transfer ins richtige Ordner !")      
        self.Transfer.btn_OK_transfer.raise_()                
        self.Transfer.lbl_speed.setStyleSheet("background-color: none;font: none;")
        self.Transfer.label_gif_transfer.setVisible(True)        
        self.movie = QMovie(str(Path(__file__).absolute().parent / "grafics/transfer.gif"))
        self.Transfer.label_gif_transfer.setMovie(self.movie) 
        self.movie.start()                         
        self.startTransfer(directory +"/"+ move_file,verschiebe_ordner +"/"+ move_file)

    def startTransfer(self, source_path: str, dest_path: str) -> None:
        self.Transfer.btn_Stop.raise_()        
        self.transferThread = FileTransferThread(source_path, dest_path)
        self.transferThread.updateProgress.connect(self.updateProgress)        
        self.transferThread.abort_signal.connect(self.transferBreak)        
        self.transferThread.finished.connect(self.transferFinished)  
        self.transferThread.start()          
        self.Transfer.btn_Stop.clicked.connect(self.transferThread.stop)   
    
    def updateProgress(self, value: int ,speed: float, remaining_time: float) -> None:
        self.Transfer.btn_OK_transfer.setEnabled(False)        
        self.Transfer.prgBar_Transfer.setValue(value) 
        minutes, seconds = divmod(remaining_time, 60)       
        self.Transfer.lbl_speed.setText(f"{speed:.2f} MB/s - geschätze Zeit bis Ende: {minutes:02d}:{seconds:02d}s")
        
    def transferBreak(self,avg_speed: float, remaining_time: float) -> None:
        self.Transfer.btn_OK_transfer.setEnabled(True)
        self.Transfer.btn_OK_transfer.raise_()  
        self.transferThread.finished.disconnect()  
        self.transferThread.quit()        
        self.movie.stop()
        self.Transfer.label_gif_transfer.setPixmap(QPixmap(str(Path(__file__).absolute().parent / "grafics/sign-error-icon.png)")))       
        Path(self.transferThread.target_path).unlink()
        minutes, seconds = divmod(remaining_time, 60) 
        self.Transfer.lbl_speed.setText(f"{avg_speed:.2f} MB/s - geschätzte Zeit bis zum Ende: {minutes:02d}:{seconds:02d}s > ABBRUCH !!!")
        
    def transferFinished(self): 
        self.Transfer.btn_OK_transfer.setEnabled(True)
        self.Transfer.btn_OK_transfer.raise_() 
        self.transferThread.quit()
        self.transferThread.wait()
        self.movie.stop()
        self.Transfer.label_gif_transfer.setPixmap(QPixmap(str(Path(__file__).absolute().parent / "grafics/Info.jpg")))
        self.Transfer.lbl_speed.setText("100 MB/s - geschätzte Zeit bis zum Ende: 00:00s > FERTIG !!!")        
        if (Path(self.transferThread.source_path).stat().st_size == Path(self.transferThread.target_path).stat().st_size
           and self.transferThread.source_path!=self.transferThread.target_path):
            Path(self.transferThread.source_path).unlink()
            row_index = self.tblWdg_Performers.currentRow()
            self.tblWdg_Files.removeRow(row_index)  
        self.Transfer.btn_OK_transfer.clicked.connect(lambda: self.ordner_transfer_zurueck(False, self.transferThread.target_path))          

    # IAFD Link Maker
    def IAFDLink(self):
        infos_webside = Infos_WebSides(MainWindow=self)
        titel = self.lnEdit_Titel.text()
        jahr = self.lnEdit_Jahr.text()
        infos_webside.IAFDLink(titel,jahr)

    # kopiere den Text welcher aktiv ist vom Datenbank Tab in die Zwischenablage        
    def CopyText(self):
        txt: str=None
        widget_name: str=None
        clip_settings = {
            "lnEdit_DBRegie" : "Director: {txt}",
            "lnEdit_DBProDate" : "Comments:\nDate of Production: {txt}",
            "lnEdit_DBRelease" : "Release Date: {txt}",
            "lnEdit_DBDauer" : "Minutes: {txt}",
            "txtEdit_DBMovies" : "Appears In:\n{txt}",
            "txtEdit_DBSynopsis" : "Synopsis:\n{txt}",
        }
        focused_widget = self.grpBox_Daten.focusWidget()  # Das aktuell fokussierte Widget

        if isinstance(focused_widget, QLineEdit):
            text = focused_widget.text()
            widget_name = focused_widget.objectName()
        elif isinstance(focused_widget, QTextEdit):
            text = focused_widget.toPlainText()
            widget_name = focused_widget.objectName()

        if text:                                                   
            if widget_name in clip_settings.keys():                
                pyperclip.copy(clip_settings[widget_name].format(txt=text))
                self.txtEdit_Clipboard.setPlainText(clip_settings[widget_name].format(txt=text))
            else: 
                pyperclip.copy(text)
                self.txtEdit_Clipboard.setPlainText(text)
        else:
            self.txtEdit_Clipboard.setPlainText("❌ kein Feld aktiv !") 

    def dialog_auswahl(self):
    # Erstellen Sie eine Instanz des Dlg_Daten_Auswahl-Dialogs
        dlg = Dlg_Daten_Auswahl(MainWindow=self)
        # Rufen Sie die exec-Methode auf, um das Dialogfenster anzuzeigen
        dlg.exec()

    
    def linksuche_in_db(self):        
        link: str = self.lnEdit_URL.text()
        studio: str = self.lnEdit_Studio.text()  

        if self.is_studio_in_database(studio):
            scraping_data = ScrapingData(MainWindow=self)
            errorview = scraping_data.hole_link_aus_db(link, studio)
            if errorview:
                MsgBox(self, errorview,"w") 
            else:                
                self.tabelle_erstellen_fuer_movie()              
                self.DB_Anzeige()
        else:
            MsgBox(self, f"Es gibt noch keine Datenbank für: <{studio}>","w")


    @pyqtSlot()
    def performer_suche(self):
        self.tblWdg_Daten.setRowCount(0)        
        if self.sender() == self.Btn_perfomsuche_in_DB:
            studio: str=self.Btn_logo_am_db_tab.toolTip()
            name_db: str=self.lnEdit_db_performer.text()
        else:             
            studio: str=self.lbl_SuchStudio.text()
            name_db: str=self.cBox_performers.currentText()                
        
        if self.is_studio_in_database(studio):
            scraping_data = ScrapingData(MainWindow=self)
            errorview: str=scraping_data.hole_link_von_performer(name_db, studio)  # erstellt auch in tblWdg_Daten die Liste          
            if errorview:
                MsgBox(self, errorview,"w") 
            else:                
                self.tabelle_erstellen_fuer_movie()
        else:
            MsgBox(self, f"Es gibt noch keine Datenbank für: <{studio}>","w")

    def datenbank_performer_suche_prevpage(self):
        if self.lnEdit_IAFD_performer.text() != "":
            page_max=int(self.lnEdit_maxpage.text())
            page = int(self.lnEdit_page.text())
            page-=1
            if page < 0:
                page= page_max
            self.lnEdit_page.setText(f"{page}")
            self.datenbank_performer_suche()
        else:
            QTimer.singleShot(100, lambda :self.lnEdit_IAFD_performer.setStyleSheet('background-color: #FF0000'))            
            QTimer.singleShot(3500, lambda :self.lnEdit_IAFD_performer.setStyleSheet('background-color:'))
    
    def datenbank_performer_suche_nextpage(self):
        if self.lnEdit_IAFD_performer.text() != "":
            page_max=int(self.lnEdit_maxpage.text())
            page = int(self.lnEdit_page.text())
            page+=1
            if page > page_max:
                page= 1
            self.lnEdit_page.setText(f"{page}")
            self.datenbank_performer_suche()
        else:
            QTimer.singleShot(100, lambda :self.lnEdit_IAFD_performer.setStyleSheet('background-color: #FF0000'))            
            QTimer.singleShot(3500, lambda :self.lnEdit_IAFD_performer.setStyleSheet('background-color:'))

    def datenbank_performer_suche(self):
        if self.sender() == self.Btn_DB_perfomer_suche:
            self.lnEdit_page.setText("1")
            self.lnEdit_maxpage.setText("1")
            self.show_performers_images = ShowPerformerImages(self)        
        performer_infos_maske=PerformerInfosMaske(MainWindow=self)
        performer_infos_maske.clear_maske()
        artist=self.lnEdit_IAFD_performer.text()        
        if len(artist) > 1:
            if artist[-1:] == "*":
                artist = f"{artist[:-1]}%"
            if artist[:1] == "*":
                artist = f"%{artist[1:]}"
        else:
            if artist == "*":
                artist = "%"
        page_number=int(self.lnEdit_page.text())
        db_for_darsteller = DB_Darsteller(MainWindow=self)
        errview = db_for_darsteller.get_all_datas_from_database(artist, page_number)
        if errview is not None:
            self.tabelle_erstellen_fuer_performer()
    
    def update_datensatz(self):
        performer_infos_maske = PerformerInfosMaske(MainWindow=self)
        performer_infos_maske.update_datensatz()

    def expand_table_links(self):
        table_widget_breite=self.tblWdg_performer_links.height()
        if table_widget_breite == 140:
            self.tblWdg_performer_links.setGeometry(30, 360, 870, 140+300)
            self.Btn_table_links_expanding.move(450, 505+300)
        else:
            self.tblWdg_performer_links.setGeometry(30, 360, 870, 140)
            self.Btn_table_links_expanding.move(450, 505)

    def expand_table_daten(self):
        table_widget_laenge=self.tblWdg_Daten.width()
        if table_widget_laenge == 890:
            self.tblWdg_Daten.setGeometry(30, 210, 890+940, 750)
            self.Btn_table_daten_expanding.move(925+940, 540)
        else:
            self.tblWdg_Daten.setGeometry(30, 210, 890, 750)
            self.Btn_table_daten_expanding.move(925, 540)

    def tabelle_erstellen_fuer_movie(self):
        zeile: int = 0
        video_data_json=VideoData().load_from_json()
        for zeile, video_data in enumerate(video_data_json):
            self.tblWdg_Daten.setRowCount(zeile+1)            
            self.tblWdg_Daten.setItem(zeile,0,QTableWidgetItem(video_data["Titel"])) 
            self.tblWdg_Daten.setItem(zeile,1,QTableWidgetItem(video_data["WebSideLink"]))
            self.tblWdg_Daten.setItem(zeile,2,QTableWidgetItem(video_data["IAFDLink"]))               
            self.tblWdg_Daten.setItem(zeile,3,QTableWidgetItem(video_data["Performers"]))
            self.tblWdg_Daten.setItem(zeile,4,QTableWidgetItem(video_data["Alias"])) 
            self.tblWdg_Daten.setItem(zeile,5,QTableWidgetItem(video_data["Action"]))
            self.tblWdg_Daten.setItem(zeile,6,QTableWidgetItem(video_data["Dauer"]))
            self.tblWdg_Daten.setItem(zeile,7,QTableWidgetItem(video_data["ReleaseDate"]))               
            self.tblWdg_Daten.setItem(zeile,8,QTableWidgetItem(video_data["ProductionDate"]))
            self.tblWdg_Daten.setItem(zeile,9,QTableWidgetItem(video_data["Serie"]))
            self.tblWdg_Daten.setItem(zeile,10,QTableWidgetItem(video_data["Regie"]))
            self.tblWdg_Daten.setItem(zeile,11,QTableWidgetItem(video_data["SceneCode"]))
            self.tblWdg_Daten.setItem(zeile,12,QTableWidgetItem(video_data["Movies"]))
            self.tblWdg_Daten.setItem(zeile,13,QTableWidgetItem(video_data["Synopsis"])) 
            self.tblWdg_Daten.setItem(zeile,14,QTableWidgetItem(video_data["Tags"]))
        self.tblWdg_Daten.setCurrentCell(zeile, 0)

    def tabelle_erstellen_fuer_performer(self):        
        zeile: int = 0
        artist_data_json=VideoData().load_from_json()
        for zeile, artist_data in enumerate(artist_data_json):            
            self.tblWdg_Daten.setRowCount(zeile+1) 
            self.tblWdg_Daten.setItem(zeile,0,QTableWidgetItem(f'{artist_data["ArtistID"]}'))           
            self.tblWdg_Daten.setItem(zeile,1,QTableWidgetItem(artist_data["Name"])) 
            self.tblWdg_Daten.setItem(zeile,2,QTableWidgetItem(artist_data["IAFDLink"]))
            self.tblWdg_Daten.setItem(zeile,3,QTableWidgetItem(artist_data["BabePedia"]))               
            self.tblWdg_Daten.setItem(zeile,4,QTableWidgetItem(f'{artist_data["Geschlecht"]}'))
            self.tblWdg_Daten.setItem(zeile,5,QTableWidgetItem(f'{artist_data["RassenID"]}')) 
            self.tblWdg_Daten.setItem(zeile,6,QTableWidgetItem(artist_data["Nation"]))
            self.tblWdg_Daten.setItem(zeile,7,QTableWidgetItem(artist_data["Geburtstag"]))
            self.tblWdg_Daten.setItem(zeile,8,QTableWidgetItem(artist_data["Birth_Place"]))
            self.tblWdg_Daten.setItem(zeile,9,QTableWidgetItem(artist_data["OnlyFans"]))               
            self.tblWdg_Daten.setItem(zeile,10,QTableWidgetItem(artist_data["Boobs"]))
            self.tblWdg_Daten.setItem(zeile,11,QTableWidgetItem(f'{artist_data["Gewicht"]}'))
            self.tblWdg_Daten.setItem(zeile,12,QTableWidgetItem(f'{artist_data["Groesse"]}'))
            self.tblWdg_Daten.setItem(zeile,13,QTableWidgetItem(artist_data["Bodytyp"]))
            self.tblWdg_Daten.setItem(zeile,14,QTableWidgetItem(artist_data["Piercing"]))
            self.tblWdg_Daten.setItem(zeile,15,QTableWidgetItem(artist_data["Tattoo"])) 
            self.tblWdg_Daten.setItem(zeile,16,QTableWidgetItem(artist_data["Haarfarbe"]))
            self.tblWdg_Daten.setItem(zeile,17,QTableWidgetItem(artist_data["Augenfarbe"]))
            self.tblWdg_Daten.setItem(zeile,18,QTableWidgetItem(artist_data["Aktiv"]))
            self.tblWdg_Daten.setItem(zeile,19,QTableWidgetItem(f'{artist_data["Geschlecht"]}'))
        self.tblWdg_Daten.setCurrentCell(zeile, 0)   

    ### ---------------------------------------------------------------------- ###
    ### ---- Infos aus der Datenbank holen, um Dateien mit Daten zu füllen --- ###
    ### ---------------------------------------------------------------------- ###
    @pyqtSlot()
    def titel_suche(self):
        self.tblWdg_Daten.setRowCount(0)        
        if self.sender() == self.Btn_Titelsuche_in_DB:
            studio: str=self.Btn_logo_am_db_tab.toolTip() 
            titel_db: str=self.lnEdit_db_titel.text().replace("'","''") 
            self.lnEdit_db_titel.setText(titel_db)
        else: 
            studio: str=self.lbl_SuchStudio.text()   
            titel_db: str=self.lnEdit_analyse_titel.text().replace("'","''") 
            self.lnEdit_db_titel.setText(titel_db) 
        if self.is_studio_in_database(studio):
            self.lnEdit_db_titel.setText(self.lnEdit_analyse_titel.text())
            scraping_data = ScrapingData(MainWindow=self)
            errorview = scraping_data.hole_titel_aus_db(titel_db, studio)
            if errorview:
                MsgBox(self, errorview,"w") 
            else:                
                self.tabelle_erstellen_fuer_movie() 
        else:
            MsgBox(self, f"Es gibt noch keine Datenbank für: <{studio}>","w")
   
    ### ---------------------------------------------------------------------------- ###
    ### ---- von Datienamen zum Titel in der DB splitten, Titel, Namen Link usw. --- ###
    ### ---------------------------------------------------------------------------- ###
    def filename_analyse(self, file_name: str) -> Tuple [str, str, str]: 
        studio: str=None
        file_name = re.sub(r"(\s)|(-)"," ",str(file_name).replace(".mp4",""))
        file_name_parts: list = file_name.split(" ")

        db_webside_settings = Webside_Settings(MainWindow=self)
        if db_webside_settings.is_studio_in_db(file_name_parts[0]):
            studio = file_name_parts[0]
            file_name = file_name.replace(studio,"").strip()
        file_name_parts=file_name.split(" ")
        file_name_parts = list(filter(lambda x: x != "", file_name_parts)) 
        name_all: list = []
        for file_name_part in file_name_parts:
            database_darsteller = DB_Darsteller(MainWindow=self)
            artist_name = database_darsteller.suche_nach_artistname(file_name_part) 
            if any(file_name_part in name for name in artist_name):
                file_name=file_name.replace(file_name_part,"").strip()
                name_all.extend(artist_name) 

        return(studio, file_name, name_all)
    
    ### ------------------------------------------------------------------------------------ ###
    ### ---- vom Basislink incl IAFD Link, gucken ob es da schon einn Eintrag für gibt ----- ###
    ### ------------------------------------------------------------------------------------ ###
    def link_isin_from_db(self): 
        link= self.lnEdit_URL.text()                 
        base_url: str = "/".join(link.split("/")[:3])
        iafdlink = link if link.startswith("https://www.iafd.com/") else None
        scraping_data  = ScrapingData(MainWindow=self)
        link_in_db = scraping_data.is_link_in_db(base_url, iafdlink) # schaut ob weblink oder iafdlink da is 
        self.Btn_addDatei.setEnabled(link_in_db)            


    def link_maker(self):
        if self.lnEdit_IAFD_titel.text()!="" and self.lnEdit_db_jahr.text()!="":            
            title=self.lnEdit_IAFD_titel.text().lower().replace(" ","+")            
            hostname=f'https://www.iafd.com/title.rme/title={title}/year={self.lnEdit_db_jahr.text()[:4]}/{title.replace("+","-")}.htm'
            pyperclip.copy(hostname)
            self.txtEdit_Clipboard.setPlainText(f"IAFD Link: \n{hostname}")

    def Web_IAFD_change(self):        
        infos_webside = Infos_WebSides(MainWindow=self)
        infos_webside.Web_IAFD_change() 

    def Web_IAFD_artist_change(self):
        iafd_infos = IAFDInfos(MainWindow=self)
        iafd_infos.check_IAFD_performer_link() 
    
    def Web_BabePedia_artist_change(self):
        pass

    def get_IAFD_performer_link(self): 
        iafd_infos = IAFDInfos(MainWindow=self)
        iafd_infos.get_IAFD_performer_link()  

    def load_IAFD_performer_link(self): 
        iafd_infos = IAFDInfos(MainWindow=self)
        iafd_infos.load_IAFD_performer_link()        

    def Web_Data18_change(self):
        infos_webside = Infos_WebSides(MainWindow=self)
        infos_webside.Web_Data18_change()  

    def webscrap_data18(self):        
        self.lbl_checkWeb_Data18URL.setVisible(True)
        infos_webside = Infos_WebSides(MainWindow=self)
        infos_webside.webscrap_data18() 
    
    def webscrap_url(self):
        self.lbl_checkWeb_URL.setVisible(True)               
        infos_webside = Infos_WebSides(MainWindow=self)
        infos_webside.webscrap_url()

    def webscrap_iafd(self):
        self.lbl_checkWeb_IAFDURL.setVisible(True)
        infos_webside = Infos_WebSides(MainWindow=self)
        infos_webside.webscrap_iafd()


    def videodaten_holen(self):
        self.stackedWidget.setCurrentIndex(1) 
        studio = self.lnEdit_Studio.text()      

        db_webside_settings = Webside_Settings(MainWindow=self) 
        errorview, links = db_webside_settings.from_studio_to_all_baselinks(studio) 
        if errorview:
            StatusBar(self, f"Error: {errorview}","#F78181")
            return
        if len(links) == 1:
            self.cBox_studio_links.addItem(links[0])            
        else:
            for link in links:                
                self.cBox_studio_links.addItem(link) 
        

    def start_spider(self):       
        baselink = self.cBox_studio_links.currentText()
        db_webside_settings = Webside_Settings(MainWindow=self)      
        errorview, spider_class_name = db_webside_settings.from_link_to_spider(baselink)
        if errorview:
            StatusBar(self, f"Error: {errorview}","#F78181")
            self.Btn_start_spider.setEnabled(False)
            return          
        settings_module = '.'.join(spider_class_name.split('.')[:-3])+'.settings'  
        my_settings = Settings()
        my_settings.setmodule(settings_module) 
        print(my_settings.get('BOT_NAME'))       
        my_settings.set('LAST_VISIT',datetime.today().strftime("%Y.%m.%d"))
        print(my_settings.get('LAST_VISIT'))
        #SpiderMonitor(spider_class_name, self)
        
    def set_iafd_button_and_tooltip(self):       
        if self.cBox_performer_sex.currentText():
            self.Btn_IAFD_perfomer_suche.setEnabled(True)
            self.Btn_IAFD_perfomer_suche.setToolTip("erstellt ein IAFD Link und setzt in die Maske")
        else:
            self.Btn_IAFD_perfomer_suche.setEnabled(False)
            self.Btn_IAFD_perfomer_suche.setToolTip("Geschlecht auswählen !")
        
    def Datei_loeschen(self):
        old_file=self.tblWdg_Files.selectedItems()[0].text()
        dir=self.lbl_Ordner.text()
        Path(dir,old_file+".mp4").unlink()
        StatusBar(self, f"gelöschte Dateiname: {old_file}","#efffb7")
        zeile=self.tblWdg_Files.currentRow()-1
        if zeile>=0:
            self.tblWdg_Files.setCurrentCell(zeile, 0)
            self.refresh_table()
        else:
            self.tblWdg_Files.clearContents()
            self.tblWdg_Files.setRowCount(0)
        self.DIA_Loeschen.hide()

    def Datei_Rename(self):
        old_file=self.tblWdg_Files.selectedItems()[0].text()+".mp4"
        new_file=self.DIA_Rename.lnEdit_Rename.text()+".mp4"
        self.lbl_Dateiname.setText(new_file)
        dir=self.lbl_Ordner.text()
        err=self.file_rename(dir,old_file,new_file)
        if err=="":
            StatusBar(self, f"Datei in {new_file} umbennant","#efffb7")#hellgelb)
            self.Info_Datei_Laden(True)
            self.DIA_Rename.hide()

    def AddArtist(self):
        self.lstWdg_Darstellerin.addItem(self.lnEdit_AddArtist.text()) 

    def move_items(self, source_list_widget: QListWidget, destination_list_widget: QListWidget) -> None:
        list_items = source_list_widget.selectedItems()
        if not list_items:
            return
        for item in list_items:
            destination_list_widget.addItem(item.text())
            source_list_widget.takeItem(source_list_widget.row(item))

    def AddLinks(self):
        self.move_items(self.lstWdg_Darsteller, self.lstWdg_Darstellerin)

    def AddRechts(self):
        self.move_items(self.lstWdg_Darstellerin, self.lstWdg_Darsteller)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self.deleteSelectedItem(self.lstWdg_Darsteller)
            self.deleteSelectedItem(self.lstWdg_Darstellerin)

    def deleteSelectedItem(self, list_widget: QListWidget) -> None:
        current_item = list_widget.currentItem()
        if current_item is not None:
            list_widget.takeItem(list_widget.currentRow())

    def Dateidatum(self,datum : str) -> str:
        datum=str(datetime.fromtimestamp(datum))
        return datum[:datum.rfind(".")]

    def datei_groesse_in_bytes(self,dir : Path, file_name: Path) -> str:
        file_size=Path(dir / file_name).stat().st_size    
        regex = re.compile("^\d*\D?\d{1,%s}|\d{1,%s}" % (3, 3))
        datei_groesse = ".".join(regex.findall(("%.1f" % file_size)[::-1]))[::-1] 
        return str(datei_groesse)[:-2]+" Bytes"

    def Info_Datei_Laden(self, refresh=False):       
        directory = Path(self.lbl_Ordner.text())
        if not refresh:
            einstellungen_ui = Einstellungen(self)
            directory = einstellungen_ui.Info_Datei()
        if directory and directory.exists() and directory.is_dir():
            self.tblWdg_Files.raise_()
            self.tblWdg_Files.clearContents()
            self.lbl_Ordner.setText(str(directory))
            supported_extensions = (".mp4", ".avi", ".mkv", ".wmv")
            zeile = 0  # Zeilennummer initialisieren

            for file in directory.iterdir():
                if file.suffix in supported_extensions:
                    datum = file.stat().st_ctime
                    self.tblWdg_Files.setRowCount(zeile + 1)
                    file_name = str(file.stem)
                    self.tblWdg_Files.setItem(zeile, 0, QTableWidgetItem(file_name))
                    file_size = self.datei_groesse_in_bytes(directory, file)
                    self.tblWdg_Files.setItem(zeile, 1, QTableWidgetItem(file_size))
                    date_formatted = self.Dateidatum(datum)
                    self.tblWdg_Files.setItem(zeile, 2, QTableWidgetItem(date_formatted))
                    self.tblWdg_Files.setItem(zeile, 3, QTableWidgetItem(file.suffix[1:]))
                    self.tblWdg_Files.item(zeile, 1).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignJustify)
                    self.tblWdg_Files.item(zeile, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignJustify)
                    zeile += 1

            self.tblWdg_Files.resizeColumnsToContents()
            self.tabs_clearing(False, False)
        else:
            if directory:
                MsgBox(self, "Datei ist nicht vorhanden!", "w")
                StatusBar(self, f"Daten: '{directory}' konnte nicht geladen werden !", "#F78181")

    def Ordner_Infos(self) -> None:
        self.tblWdg_Files.setCurrentCell(self.tblWdg_Files.currentRow(),0)
        try:
            self.lbl_Dateiname.setText(self.tblWdg_Files.selectedItems()[0].text()+".mp4")
            self.tabs.setCurrentIndex(0)
            einstellung_ui = Einstellungen(self)
            if einstellung_ui.chkBox_InfosExifTool.isChecked():
                self.Infos_ExifToolHolen()
        except IndexError:
            self.tblWdg_Files.clearContents() 

    def Websides_Auswahl(self):        
        logo_button=self.sender().whatsThis()
        self.WebSide = uic.loadUi(BUTTONS_WEBSIDES_UI)
        self.WebSide.Btn_Zurueck.clicked.connect(self.WebSide.hide)
        buttons = json.loads(BUTTONSNAMES_JSON_PATH.read_bytes())               
        for button in buttons["Buttons"]: 
            try:                          
                self.WebSide.findChild(QPushButton,'Btn_{}'.format(button)).clicked.connect(lambda: self.Websides(logo_button))
            except AttributeError:
                print(button)                        
        self.WebSide.exec()
         
    def Websides(self, logo_button: str, button: str = None) -> None:
        if logo_button:
            button = self.sender().whatsThis()
            self.WebSide.hide()             
        db_webside_settings = Webside_Settings(MainWindow=self)        
        errorview, studio, logo=db_webside_settings.get_buttonlogo_from_studio(button)
        if logo_button=="Datei-Info" or logo_button=="Analyse": 
            self.cBox_studio_links.clear()           
            self.Btn_logo_am_infos_tab.setToolTip(studio)
            self.Btn_logo_am_infos_tab.setStyleSheet(logo)
            self.Btn_logo_am_analyse_tab.setToolTip(studio)
            self.Btn_logo_am_analyse_tab.setStyleSheet(logo)             
            self.lnEdit_Studio.setText(studio)
            self.lbl_SuchStudio.setText(studio)                
            self.Btn_VideoDatenHolen.setEnabled(True)
            self.lnEdit_Studio.setText(studio)
            if not studio:            
                self.Btn_VideoDatenHolen.setEnabled(False)
                self.lnEdit_Studio.setText("")             
        else:    
            self.Btn_logo_am_db_tab.setStyleSheet(logo)
            self.Btn_logo_am_db_tab.setToolTip(studio)    
            self.Btn_DBUpdate.setEnabled(bool(self.lnEdit_DBTitel.text())) ### wenn "" deaktiv
            self.Btn_addDatei.setEnabled(bool(self.lnEdit_DBTitel.text())) ### wenn !="" aktiv


    def einstellungen_ui_show(self):                  
        einstellungen_ui = Einstellungen(self)
        einstellungen_ui.show()

    def ordner_transfer_zurueck(self,save: bool, target_path: str=None) -> None:
        if hasattr(self, 'Transfer'):
            self.Transfer.reject()
        errorview, movies = None, None
        if save:
            process_output = json.loads(PROCESS_JSON_PATH.read_bytes())         
            if self.rdBtn_rename.isChecked():
                errview=self.file_rename(self.lbl_Ordner.text(),process_output["old_file"],"")                           
            else:                
                errview=self.file_rename(self.lbl_Ordner.text(),process_output["old_file"],process_output["new_file"])             
        else:                    
            move_file = self.lbl_Dateiname.text()
            error = self.load_exiftool_json(target_path)
            if not error and MEDIA_JSON_PATH.exists():
                with open(MEDIA_JSON_PATH,'r') as file:
                    file_media_info = json.loads(file.read())[0]
                movies=file_media_info.get("Genre","").strip().split("\n")
                studio=file_media_info.get("Publisher","")                
                db_webside_settings = Webside_Settings(MainWindow=self) 
                errorview,verschiebe_ordner = db_webside_settings.hole_verschiebe_ordner(studio)  
                if not errorview:
                    self.make_simlink(movies,verschiebe_ordner,move_file)         
            else:
                MsgBox(self, error,"w")  
        self.tblWdg_Files.update() 

    
    def windows_file_filter(self, file_name):
        # Definieren Sie einen regulären Ausdruck, um ungültige Zeichen zu finden
        invalid_chars_pattern = r"[^-a-zA-Z0-9_äöü.,()&+#!\[\] ?*]+" # <-- [':', '"', '/', '\\', '|', '?', '*']        
        # Entfernen Sie ungültige Zeichen aus dem Dateinamen
        cleaned_file_name = re.sub(invalid_chars_pattern, '', file_name.strip())
        return cleaned_file_name

    def make_simlink(self,movies,verschiebe_ordner,move_file):
        if not movies[0]:
            return        
        for movie_name in movies:                                    
            # Den Pfad zum übergeordneten Ordner abrufen
            einsvor_verschiebe_ordner = Path(verschiebe_ordner).parent
            if movie_name.find(": ") == -1:
                ziel_verzeichnis = einsvor_verschiebe_ordner
                dateiname = f"{movie_name.strip()}.mp4.lnk"                
                symlink_meldung = f'/ Symlink >{dateiname}.lnk< erstellt !'
            else:
                scene_nr = movie_name[6:movie_name.find(": ")] + "_"
                movie_name = movie_name[movie_name.find(": ") + 2:]
                
                if Path(verschiebe_ordner, "_Movies").exists():
                    ziel_verzeichnis = Path(verschiebe_ordner, "_Movies", movie_name.strip())
                elif Path(einsvor_verschiebe_ordner, "_Movies").exists():
                    ziel_verzeichnis = Path(einsvor_verschiebe_ordner, "_Movies", movie_name.strip())
                else:
                    ziel_verzeichnis = None
                
                dateiname = f"{scene_nr}{move_file}.lnk"
                symlink_meldung = f'/ Symlink >{dateiname}< erstellt !'

            if ziel_verzeichnis:
                dateiname = self.windows_file_filter(dateiname)
                ziel_symlink = ziel_verzeichnis / dateiname
                ziel_symlink.parent.mkdir(parents=True, exist_ok=True)  # Erstelle Verzeichnis rekursiv
                symlink_meldung = f'/ Symlink >{ziel_symlink}< erstellt !'            

            # Erstelle den Symbolic Link            
            shell = win32com.client.Dispatch("WScript.Shell")
            link = shell.CreateShortcut(str(ziel_symlink))
            link.TargetPath = verschiebe_ordner +"\\"+ move_file
            try:
                link.Save()
            except Exception as e:
                symlink_meldung=f"Fehler beim Erstellen des Symlinks: {e}"
            StatusBar(self, f"Datei {move_file} wird in {verschiebe_ordner} verschoben ... Fertig !!{symlink_meldung}","#efffb7")       
        
    def AddLinks(self):
        listItems=self.lstWdg_Darsteller.selectedItems()
        if not listItems: return        
        for item in listItems: 
            self.lstWdg_Darstellerin.addItem(item.text())
            self.lstWdg_Darsteller.takeItem(self.lstWdg_Darsteller.row(item))  
  
    def DarstellerZusammen(self):        
        Darsteller,Darstellerin,und=("","","")
        for item in range(self.lstWdg_Darstellerin.count()):
            Darstellerin+=self.lstWdg_Darstellerin.item(item).text()+", "
        for item in range(self.lstWdg_Darsteller.count()):
            Darsteller+=self.lstWdg_Darsteller.item(item).text()+"(m), "
            und=" & "
        d=Darstellerin[:-2]
        if d.find(", ")!=-1 and und=="":
            d=d[:d.rfind(", ")]+" & "+d[d.rfind(", ")+2:]               
        return d+und+Darsteller[:-2]

    def Infos_Speichern(self):        
        old_file=self.lbl_Dateiname.text()
        new_file=self.windows_file_filter(self.lbl_Dateiname.text())
        process_output={"stdout": "",
                        "stderr": "",
                        "old_file":old_file,
                        "new_file":new_file}            
        json.dump(process_output,open(PROCESS_JSON_PATH,'w'),indent=4, sort_keys=True)
        isda=self.addPerformer_wenn_da()                
        StatusBar(self, f"Fertig ! / {process_output['stderr']} / Es sind {isda} Darsteller in die DB hinzugefügt worden","#f3f0ff")        
        directory=self.lbl_Ordner.text()

        directory_filename=Path(directory,new_file) 
        err=self.file_rename(directory,old_file,new_file) 
        if Path(directory_filename).exists and not err:
            StatusBar(self, "speichere Daten - Warte !","#efffa7")               
            datum=self.check_Datum(self.lnEdit_ProJahr.text())
            artist=self.DarstellerZusammen().replace(" & ","/").replace(", ","/")                                         
            command=[EXIFTOOLPFAD,
                '-m', # The -m option ignores minor errors and warnings
                '-overwrite_original',
                f'-Quicktime:CreateDate={self.lnEdit_ErstellDatum.text()}',
                f'-ContentCreateDate#={datum}',
                f'-Microsoft:Director={self.lnEdit_Regie.text()}',
                f'-Microsoft:PromotionURL={self.lnEdit_IAFDURL.text()}',
                f'-Microsoft:AuthorURL={self.lnEdit_URL.text()}',
                f'-Microsoft:Writer={self.lnEdit_ProDate.text()}',                                
                f'-Microsoft:Publisher={self.lnEdit_Studio.text()}',
                f'-Microsoft:Producer={self.lnEdit_NebenSide.text()}',
                f'-Microsoft:EncodedBy={self.lnEdit_Data18URL.text()}',                                             
                f'-Microsoft:Category={self.txtBrw_Tags.toPlainText().strip()}',
                f'-Microsoft:InitialKey={self.lnEdit_SceneCode.text()}',
                f'-ItemList:Artist={artist}',
                f'-ItemList:Title={self.lnEdit_Titel.text()}',             
                f'-ItemList:Comment={self.txtBrw_Beschreibung.toPlainText().strip()}',
                f'-ItemList:Genre={self.txtBrw_Movies.toPlainText().strip()}',       
                str(directory_filename)] 
            self.Transfer = uic.loadUi(TRANSFER_UI) 
            self.Transfer.btn_OK_exif.setEnabled(True)
            self.Transfer.btn_OK_exif.raise_()
            self.movie = QMovie(str(Path(__file__).absolute().parent / "grafics/exiftool_processing.gif")) 
            self.Transfer.lbl_Dest_Folder.setText("")
            self.Transfer.setWindowTitle("Speichern von MetaTags mit Hilfe von ExifTool !")
            self.Transfer.label_gif_transfer.setMovie(self.movie)
            self.movie.start()        
            self.Transfer.lbl_move_file.setText(new_file)                             
            self.Transfer.lbl_Source_Folder.setText(directory)             
            self.Transfer.prgBar_Transfer.setValue(0)
            self.Transfer.show()             
            self.startExifSave(directory_filename,command)             
        else:
            StatusBar(self, f"Fehler ! / Datei ist nicht vorhanden !","#F78181")
            MsgBox(self, "Datei ist nicht vorhanden !","w")
    
    def addPerformer_wenn_da(self)-> bool:
        isda: int=0
        database_darsteller = DB_Darsteller(MainWindow=self)
        name_data={"Name":None,
                "Geschlecht": 0,
                "Nation":None,
                "ArtistLink":None,
                "ImagePfad":None   }
        for item in range(self.lstWdg_Darstellerin.count()):
            name=self.lstWdg_Darstellerin.item(item).text() 
            name_data["Name"]=name
            name_data["Geschlecht"]=1                                               
            artist_neu,sex_neu,link_neu=database_darsteller.addDarsteller_in_db(name_data, self.lnEdit_Studio.text())
            isda+=artist_neu                 
        for item in range(self.lstWdg_Darsteller.count()):
            name=self.lstWdg_Darsteller.item(item).text() 
            name_data["Name"]=name
            name_data["Geschlecht"]=2                        
            artist_neu,sex_neu,link_neu=database_darsteller.addDarsteller_in_db(name_data, self.lnEdit_Studio.text())
            isda+=artist_neu
        return isda

    def single_DBupdate(self):
        link_items: list = []
        infos_webside = Infos_WebSides(MainWindow=self)

        for index in range(self.model_database_weblinks.rowCount()):
            item = self.model_database_weblinks.data(self.model_database_weblinks.index(index, 0))
            link_items.append(item) 
        WebSideLink="\n".join(link_items)

        if self.tabs.currentIndex() == 2:        
            studio=self.Btn_logo_am_db_tab.toolTip()
        else:
            studio=self.Btn_logo_am_infos_tab.toolTip()                       
        infos_webside.update_db_and_ui(studio, WebSideLink) 

    
    def DB_Anzeige(self):
        infos_webside = Infos_WebSides(MainWindow=self)
        current_index = self.stackedWidget.currentIndex()
        self.tblWdg_Daten.itemSelectionChanged.connect(infos_webside.select_whole_row) # aktiviert die komplette Zeile 
        if current_index == self.stackedWidget.indexOf(self.stacked_IAFD_artist):
            self.Btn_DBArtist_Update.setEnabled(False)
            felder = ["sex", "rasse", "nation", "haar", "augen", "geburtsort", "geburtstag", "boobs", "bodytyp", "aktiv", "groesse",
                "gewicht", "piercing", "tattoo"]
            self.tooltip_claering(felder)
            performer_infos_maske = PerformerInfosMaske(MainWindow=self)
            performer_infos_maske.artist_infos_in_maske()
        elif current_index == self.stackedWidget.indexOf(self.stacked_IAFD_Linkmaker or self.stacked_db_abfrage):
            ### ----- kompette Maske löschen incl. json Infos ------- ### 
            self.datenbank_save("delete")
            felder = ["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Movies", "Synopsis", "Tags"]
            self.tooltip_claering(felder)
            self.model_database_weblinks.clear()
            self.tblWdg_Performers.clear()

            self.tabs.setCurrentIndex(2) # Tab für Datenbank aktiv
            self.tblWdg_Daten.selectRow(self.tblWdg_Daten.currentRow())
            self.lnEdit_DBTitel.setText(self.tblWdg_Daten.selectedItems()[0].text()) 

            infos_webside = Infos_WebSides(MainWindow=self)
            infos_webside.DB_Anzeige()

            self.enabled_db_buttons(True)

    def tooltip_claering(self, felder: list, artist: bool=False) -> None: 
        combo_box_widget=None 
        Line_edit_widget=None 
        text_edit_widget=None 

        for feld in felder: 
            if artist:
                combo_box_widget = self.findChild(QComboBox, f'cBox_performer_{feld}')
                Line_edit_widget = self.findChild(QLineEdit, f'lnEdit_performer{feld}')
                text_edit_widget = self.findChild(QTextEdit, f'txtEdit_performer{feld}')
            else:
                Line_edit_widget = self.findChild(QLineEdit, f'lnEdit_DB{feld}')
                text_edit_widget = self.findChild(QTextEdit, f'txtEdit_DB{feld}')                
            if Line_edit_widget or text_edit_widget or combo_box_widget:
                widget_obj = Line_edit_widget or text_edit_widget or combo_box_widget
                widget_obj.setToolTip("")

    def addLink(self):        
        link = self.lnEdit_addLink.text()
        zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
        if link.startswith("https://"):
            self.Btn_Linksuche_in_URL.setEnabled(True)
            item = QStandardItem(link)
            self.model_database_weblinks.appendRow(item)
            self.lnEdit_addLink.clear()
            self.lbl_db_status.setText(f"{zeit}: {link} hinzugefügt worden !")            
        elif link == "*":
            empty_item = QStandardItem("")
            self.model_database_weblinks.insertRow(0, empty_item)
            self.lnEdit_addLink.clear()
            self.lbl_db_status.setText(f"{zeit}: Leeren Link hinzugefügt worden !")
        else:
            self.lnEdit_addLink.setStyleSheet('background-color: red')
            self.lbl_db_status.setStyleSheet('background-color: red')
            self.lbl_db_status.setText(f"{zeit} Fehler: »{link}« ist kein Link !")
            
            QTimer.singleShot(2000, lambda :self.lnEdit_addLink.setStyleSheet('background-color: #fffdd5'))
            QTimer.singleShot(2000, lambda :self.lbl_db_status.setStyleSheet(''))
            

    def delete_link_from_listview(self):
        selected = self.lstView_database_weblinks.selectedIndexes()
        zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
        if selected:
            index = selected[0]
            row = index.row()
            if row < self.model_database_weblinks.rowCount():
                # Entferne das ausgewählte Element aus dem Modell
                self.model_database_weblinks.removeRow(row)
                selected_item = self.model_database_weblinks.item(row)
                if selected_item is not None:
                    selected_text = selected_item.text()
                else:
                    selected_text = "Leeren Link"
                    self.Btn_Linksuche_in_URL.setEnabled(False)
                self.lbl_db_status.setText(f"{zeit}: »{selected_text}« wurde gelöscht !")
            else:
                self.lbl_db_status.setText(f"{zeit}: Ungültige Auswahl.")
        else:
            self.lbl_db_status.setText(f"{zeit}: Kein Element ausgewählt.")


    def add_performers(self,name: str="",alias: str="",action: str="") -> None:
        self.tblWdg_Performers.setRowCount(self.tblWdg_Performers.rowCount()+1) 
        self.tblWdg_Performers.setItem(self.tblWdg_Performers.rowCount()-1,0,QTableWidgetItem(name))
        self.tblWdg_Performers.setItem(self.tblWdg_Performers.rowCount()-1,1,QTableWidgetItem(alias))       
        self.tblWdg_Performers.setItem(self.tblWdg_Performers.rowCount()-1,2,QTableWidgetItem(action))
        self.tblWdg_Performers.setCurrentCell(self.tblWdg_Performers.rowCount()-1, 0)
    
    def del_performers(self):
        row_index = self.tblWdg_Performers.currentRow()
        if row_index >= 0:
            self.tblWdg_Performers.removeRow(row_index)

    def add_db_in_datei(self):
        Performers: list=[]
        logo: str=self.Btn_logo_am_db_tab.styleSheet()
        studio: str=self.Btn_logo_am_db_tab.toolTip()

        self.tabs.setCurrentIndex(0)         
        self.lnEdit_Studio.setText(studio)
        self.lbl_SuchStudio.setText(studio)
        self.cBox_studio_links.clear()       
        self.Btn_logo_am_infos_tab.setToolTip(studio)
        self.Btn_logo_am_infos_tab.setStyleSheet(logo)
        self.Btn_logo_am_analyse_tab.setToolTip(studio)
        self.Btn_logo_am_analyse_tab.setStyleSheet(logo)

        for zeile in range(self.tblWdg_Performers.rowCount()):
            Performers.append(self.tblWdg_Performers.item(zeile, 0).text()) 
        self.addDarsteller_in_ui(Performers)

        self.lnEdit_Titel.setText(self.lnEdit_DBTitel.text())
        self.lnEdit_URL.setText(self.lstView_database_weblinks.model().data(self.lstView_database_weblinks.model().index(0, 0)))
        self.lnEdit_ErstellDatum.setText(self.lnEdit_DBRelease.text())
        self.lnEdit_Data18URL.setText(self.lnEdit_DBData18Link.text() if self.lnEdit_DBData18Link.text() != "" else self.lnEdit_Data18URL.text())        
        self.lnEdit_IAFDURL.setText(self.lnEdit_DBIAFDLink.text())
        self.lnEdit_ProJahr.setText(self.lnEdit_DBProDate.text()[:4] if not self.lnEdit_DBProDate.text() else self.lnEdit_DBRelease.text()[:4])
        self.lnEdit_ProDate.setText(self.lnEdit_DBProDate.text())
        self.lnEdit_NebenSide.setText(self.lnEdit_DBSerie.text().replace(" ",""))        
        self.lnEdit_Regie.setText(self.lnEdit_DBRegie.text()) 
        self.txtBrw_Movies.setText(self.txtEdit_DBMovies.toPlainText())       
        self.lnEdit_SceneCode.setText(self.lnEdit_DBSceneCode.text())                
        self.txtBrw_Beschreibung.setText(self.txtEdit_DBSynopsis.toPlainText()+"\n"+self.txtEdit_DBMovies.toPlainText())      
        self.txtBrw_Tags.setText(self.txtEdit_DBTags.toPlainText())        

    def startExifSave(self,source_path: str, command: str) -> None:
        self.Transfer.btn_OK_exif.setEnabled(False)        
        self.ExifSaveThread = ExifSaveThread(source_path,command)
        self.ExifSaveThread.Exif_Progress.connect(self.Exif_Progress) 
        self.ExifSaveThread.finished.connect(self.Exif_finished)  
        self.ExifSaveThread.start()          

    def Exif_Progress(self, value : int, speed : float, remaining_time : int , start_time :int) -> None:
        self.Transfer.btn_OK_exif.setEnabled(False)        
        self.Transfer.prgBar_Transfer.setValue(value) 
        minutes, seconds = divmod(remaining_time, 60)
        minutes_start, seconds_start = divmod(start_time, 60)       
        self.Transfer.lbl_speed.setText(f"{speed:.2f} MB/s - geschätze Zeit bis Ende: {minutes:02d}:{seconds:02d}s von {minutes_start:02d}:{seconds_start:02d}s")
        
    def Exif_finished(self, speed: int, start_time: int) -> None:                        
        process_output = json.loads(PROCESS_JSON_PATH.read_bytes())
        if process_output.get('stderr'):
            self.Transfer.hide()
            StatusBar(self, f"Fehler ! / {process_output['stderr']}","#F78181")  #hellrot        
            MsgBox(self, process_output['stderr'],"w")
        self.Transfer.btn_OK_exif.setEnabled(True)
        self.Transfer.prgBar_Transfer.setValue(100)
        self.ExifSaveThread.quit()        
        self.movie.stop()
        self.Transfer.label_gif_transfer.setPixmap(QPixmap(str(Path(__file__).absolute().parent / "grafics/Info.jpg"))) 
        minutes_start, seconds_start = divmod(start_time, 60)        
        self.Transfer.lbl_speed.setText(f"{speed:.2f} MB/s - nach Ende: {minutes_start:02d}:{seconds_start:02d}s > FERTIG ! {process_output['stdout']}")
        self.Transfer.btn_OK_exif.clicked.connect(lambda: self.ordner_transfer_zurueck(True))
         
        
    def check_Datum(self,datum : str) -> str:
        if datum:
            datum=str(self.lnEdit_ErstellDatum.text())[:4]       
        return ("20"+datum)[-4:] 
    
    def file_rename_from_infos(self):
        self.file_rename(self.lbl_Ordner.text(),self.lbl_Dateiname.text(),"")


    def file_rename(self, directory: str, old_file: str, new_file: str = "") -> str:        
        err: str=None

        if old_file == new_file:
            return err

        studio: str  = self.lnEdit_Studio.text()
        titel: str = self.lnEdit_Titel.text()
        neben_side = f"[{self.lnEdit_NebenSide.text().replace(' ', '')}]" if self.lnEdit_NebenSide.text() else ""

        if studio == "GirlCum" and "Orgasms" in titel or studio == "NubilesPorn":
            titel = titel.replace(" - ", "[") + "]"

        if studio:
            studio = studio + " - "
            
        if not new_file:
            new_file = studio + self.windows_file_filter(self.DarstellerZusammen().replace("(m)", "").replace("-", "")+"-" + titel + neben_side) + ".mp4"
            
            process_output = json.loads(PROCESS_JSON_PATH.read_bytes())
            process_output["new_file"] = new_file
            json.dump(process_output, open(PROCESS_JSON_PATH, 'w'), indent=4, sort_keys=True)

        try:
            Path(directory, old_file).rename(Path(directory, new_file))
        except OSError as os_err:
            if os_err.winerror == 32:
                os_err = "Die Datei ist noch geöffnet, bitte schließen!"
            MsgBox(self, f"Fehler !<br>{os_err}</br>", "i")
            return str(os_err)
        else:
            self.lbl_Dateiname.setText(new_file)
            self.refresh_table(new_file)
            
        return err

    def Infos_ExifToolHolen(self) -> None:        
        self.tabs_clearing(False, False) 
        filename=self.lbl_Dateiname.text()
        self.lbl_datei_info_fuer.setText(filename)       
        directory_filename = Path(self.lbl_Ordner.text(), filename)
        
        error = self.load_exiftool_json(directory_filename) 

        if not error and MEDIA_JSON_PATH.exists():
            self.metatags_in_ui_laden()

            db_webside_settings = Webside_Settings(MainWindow=self)
            errorview, studio, logo = db_webside_settings.get_buttonlogo_from_studio(self.lnEdit_Studio.text())
            if not studio:
                logo="background-image: url(':/Buttons/grafics/no-logo_90x40.jpg')"
                studio="kein Studio ausgewählt !"
            self.is_studio_in_database(studio)
            self.cBox_studio_links.clear()
            self.Btn_logo_am_infos_tab.setStyleSheet(logo)
            self.Btn_logo_am_infos_tab.setToolTip(studio)                
        else:
            MsgBox(self, error,"w") 

        
    def load_exiftool_json(self, directory_filename: str) -> str:
        error = None
        if MEDIA_JSON_PATH.exists() and MEDIA_JSON_PATH.is_file():
            MEDIA_JSON_PATH.unlink()
        try:
            process = subprocess.run([EXIFTOOLPFAD,"-json",str(directory_filename),'-W+!',str(MEDIA_JSON_PATH)], capture_output=True, text=True)        
        except subprocess.CalledProcessError as error:
            MsgBox(self, error,"w")
        return error

    def metatags_in_ui_laden(self):
        with open(MEDIA_JSON_PATH,'r') as file:
            file_media_info = json.loads(file.read())[0]        
        performers = file_media_info.get("Artist")                
        if performers:                     
            Darsteller, Darstellerin = ([i[:-3] for i in performers.split("/") if "(m)" in i],\
                                            [i for i in performers.split("/") if "(m)" not in i])
            Darsteller.extend(Darstellerin)                    
            self.addDarsteller_in_ui(Darsteller)                    
        atom_dict ={"AuthorURL":self.lnEdit_URL,
                    "Director":self.lnEdit_Regie,
                    "PromotionURL":self.lnEdit_IAFDURL,
                    "Producer":self.lnEdit_NebenSide,
                    "Publisher":self.lnEdit_Studio,
                    "Writer":self.lnEdit_ProDate,
                    "ContentDistributor":self.lnEdit_SceneCode,                                                      
                    "ContentCreateDate":self.lnEdit_ProJahr,
                    "CreateDate":self.lnEdit_ErstellDatum,
                    "InitialKey":self.lnEdit_SceneCode,
                    "Comment":self.txtBrw_Beschreibung,
                    "Category":self.txtBrw_Tags,
                    "Genre":self.txtBrw_Movies,                            
                    "Title":self.lnEdit_Titel,
                    "MediaDuration":self.lbl_Dauer,                            
                    "FileCreateDate":self.lbl_FileCreation,
                    "FileSize":self.lbl_FileSize,
                    "MajorBrand":self.lbl_VideoArt,
                    "ImageSize":self.lbl_Resize,
                    "VideoFrameRate":self.lbl_FrameRate,
                    "AvgBitrate":self.lbl_Bitrate,                            
                    "EncodedBy":self.lnEdit_Data18URL,      }
        for atom,item in atom_dict.items(): 
            if file_media_info.get(atom):                                                                
                inhalt=file_media_info.get(atom)                    
                item.setText(str(inhalt))

    
    def set_analyse_daten(self):
        self.buttons_enabled(False, ["logo_am_analyse_tab", "name_suche", "titel_suche"])

        filename: str=self.lbl_Dateiname.text()

        self.lbl_analyse_fuer.setText(filename)        
        studio_name, titel, artist=self.filename_analyse(filename)
        self.grpBox_analyse_name.setTitle(f"Darstellername:       Anzahl: {len(artist)}")

        db_webside_settings = Webside_Settings(MainWindow=self)               
        errorview, studio, logo = db_webside_settings.get_buttonlogo_from_studio(studio_name)

        if artist:
            self.buttons_enabled(True, ["logo_am_analyse_tab", "name_suche"])
            self.cBox_performers.clear()
            for item in artist:
                self.cBox_performers.addItem(item)                                           
            
            self.is_studio_in_database(studio)

        if studio:                    
            self.Btn_logo_am_analyse_tab.setEnabled(True)
            self.lbl_SuchStudio.setText(studio)                   
            self.Btn_logo_am_analyse_tab.setStyleSheet(logo)
            self.Btn_logo_am_analyse_tab.setToolTip(studio)
            self.buttons_enabled(True, ["logo_am_analyse_tab", "name_suche", "titel_suche"])

            if titel:
                self.lnEdit_analyse_titel.setText(titel)
                self.Btn_titel_suche.setEnabled(True) 
        else:
            logo="background-image: url(':/Buttons/grafics/no-logo_90x40.jpg')"
            studio="kein Studio ausgewählt !"
            self.lnEdit_analyse_titel.setText(studio)

    def is_studio_in_database(self, studio: str) -> bool:
        studio_isin: bool = False

        scraping_data = ScrapingData(MainWindow=self)
        studio_isin = scraping_data.is_studio_in_db(studio)

        if studio_isin:
            self.buttons_enabled(True,["VideoDatenHolen"])
            if studio in ["BangBros"]:
                self.special_infos_visible(True)
            else:
                self.special_infos_visible(False)
        else:
            self.buttons_enabled(False,["VideoDatenHolen"])

        return studio_isin
        

    ### Elemente ausschalten, sichtbar, unsichtbar machen, um unnötige Abfragen zu verhindern ###
    def tabs_clearing(self, tab_dateiinfo: bool=True, tab_fileinfo: bool=True, analyse_button: bool=True, table_files: bool=True) -> None:        
        if not tab_dateiinfo:
            line_edits=["Studio", "URL", "IAFDURL", "Titel", "Data18URL", "NebenSide", "ErstellDatum", "ProJahr", "ProDate", "Regie", "SceneCode"]
            list_widgets=["Darstellerin","Darsteller"]
            text_edits=["Tags","Beschreibung","Movies"]

            for line_edit in line_edits:
                getattr(self, f"lnEdit_{line_edit}").clear()

            for list_widget in list_widgets:
                getattr(self, f"lstWdg_{list_widget}").clear()

            for text_edit in text_edits:
                getattr(self, f"txtBrw_{text_edit}").clear()

            self.lbl_datei_info_fuer.clear()

        if not table_files:
            self.tblWdg_Files.clearContents()

        if not tab_fileinfo:
            labels=["Bitrate", "FrameRate", "VideoArt", "FileCreation", "FileSize", "Resize", "Dauer"]
            
            for label in labels:
                getattr(self, f"lbl_{label}").clear()

        if not analyse_button:    
            self.lbl_SuchStudio.clear()
            self.Btn_logo_am_analyse_tab.setStyleSheet("background-image: url(':/Buttons/grafics/no-logo_90x40.jpg')")
            self.Btn_logo_am_analyse_tab.setToolTip("kein Studio ausgewählt !")
                    
        if not (tab_dateiinfo and table_files and analyse_button and table_files): 
            self.cBox_studio_links.clear() 
            self.Btn_logo_am_infos_tab.setStyleSheet("background-image: url(':/Buttons/grafics/no-logo_90x40.jpg')") 
            self.Btn_logo_am_infos_tab.setToolTip("kein Studio ausgewählt !")
            self.Btn_logo_am_db_tab.setStyleSheet("background-image: url(':/Buttons/grafics/no-logo_90x40.jpg')")
            self.Btn_logo_am_db_tab.setToolTip("kein Studio ausgewählt !") 
            self.buttons_enabled(False, ["Laden", "Speichern", "Refresh"])

        if self.lbl_Dateiname.text()!="":self.Btn_Speichern.setEnabled(True)


    def enabled_db_buttons(self, bolean: bool) -> None: 
        webside_model = self.lstView_database_weblinks.model()
        data18 = self.lnEdit_DBData18Link
        iafd = self.lnEdit_DBIAFDLink
        
        self.Btn_Linksuche_in_URL.setEnabled(webside_model and bolean)
        self.Btn_Linksuche_in_Data18.setEnabled(bool(data18.text()) and bolean)
        self.Btn_Linksuche_in_IAFD.setEnabled(bool(iafd.text()) and bolean)

        self.Btn_addDatei.setEnabled(bolean)
        self.Btn_DBUpdate.setEnabled(bolean)
            

    def buttons_enabled(self, bolean: bool, buttons: list) -> None:        
        for info in buttons:
            getattr(self,f"Btn_{info}").setEnabled(bolean)

    ### Seiten wie Bangbros zusätliche Infos sichtbar machen ###
    def special_infos_visible(self, bolean: bool) -> None:
        infos=[self.lblSceneCode,
            self.lnEdit_SceneCode,
            self.lblProDate,
            self.lnEdit_ProDate,
            self.lblRegie,
            self.lnEdit_Regie,   ]
        for info in infos:
            info.setVisible(bolean)

    def addDarsteller_in_ui(self, performers: list) -> None:
        if self.tabs.currentWidget() == self.tab_info:
            widget_variable_w = self.lstWdg_Darstellerin
            widget_variable_m = self.lstWdg_Darsteller
            widget_variable_w.clear()
            widget_variable_m.clear()            
            custom_widget = QWidget()            
            custom_widget.setAutoFillBackground(True)
            database_darsteller = DB_Darsteller(MainWindow=self)
            for performer in performers:
                item = QListWidgetItem(performer)                
                is_vorhanden, geschlecht = database_darsteller.isdaDarsteller(performer)                
                if is_vorhanden and geschlecht > 1:
                    item.setBackground(QBrush(QColor("#e9ff1d")))
                    widget_variable_m.addItem(item)
                else:
                    item.setBackground(QBrush(QColor("#e9ff1d"))) 
                widget_variable_w.addItem(item)                     
 

    def gui_last_side(self):                
        studio: str = self.lnEdit_Studio.text()
        last_side: int = 2

        if studio:
            db_webside_settings = Webside_Settings(MainWindow=self)
            errorview, links = db_webside_settings.from_studio_to_all_baselinks(studio)
            if errorview:
                MsgBox(self, f"Fehler beim Basis-Link holen: {errorview} / Abbruch !" ,"w")
                return
            if len(links) == 1:
                 self.cBox_studio_links.setCurrentText(links[0])
            else:
                for link in links:                
                    self.cBox_studio_links.addItem(link)

            baselink = self.cBox_studio_links.currentText()
            if baselink is None: 
                message= "Link aus der ComboBox auswählen !"
                self.status_fehler_ausgabe(self, message)
                self.cBox_studio_links.setFocus()
            errorview, last_visite = db_webside_settings.get_lastVisite(baselink)
            if errorview:
                StatusBar(self, f"Fehler: {errorview}","#F78181") 

            if self.rdBtn_last_side_von_DB.isChecked():                
                errorview, last_page_number = db_webside_settings.get_last_side_from_db(baselink)
                if errorview:
                    StatusBar(self, "Fehler beim Holen der letzten Page Nummer aus der Datenbank","#F78181")
            else:
                websides = Infos_WebSides(MainWindow=self)
                last_page_number = websides.get_last_page_from_webside(baselink) 

            db_webside_settings.add_lastVisite(baselink, datetime.now().strftime("%Y %m %d %H:%M"))

            self.spinBox_bisVideo.setValue(last_page_number) 
            StatusBar(self, f"letzte Seite von ({studio}) '{baselink}' hat nun {last_page_number} als letzte Video Side erfasst !","#ffea9e")

        else:
            message= "Bitte die Porno Seite / Studio angeben !"
            status_fehler_ausgabe(self, message)  
    

# Abschluss
if __name__ == '__main__':
    app, MainWindow =(QApplication(sys.argv), Haupt_Fenster())   
    ## ------- Erstellen eines QTranslator-Objekts -------- ##
    translator = QTranslator()   
    translator.load("qt_de.qm")# deutsch setzen
    app.installTranslator(translator) 
    ## ---------------------------------------------------- ## 
    MainWindow.show()   
    sys.exit(app.exec())

