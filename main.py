from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTranslator, QVariantAnimation, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QAbstractItemView, QTableWidgetItem, QApplication, QPushButton, QWidget, QListWidgetItem , \
    QListWidget, QLineEdit, QTextEdit, QTableWidget, QMenu
from PyQt6.QtGui import QMovie, QPixmap, QKeyEvent, QStandardItem, QStandardItemModel, QColor, QBrush, QIcon
from PyQt6.QtTest import QTest



import sys
import json
import subprocess
import re
import errno
from datetime import datetime
import pyperclip
import win32com.client
from pathlib import Path
from typing import List, Tuple
from scrapy.settings import Settings
from urllib.parse import urlparse
from functools import partial

import gui.resource_collection_files.logo_rc
import gui.resource_collection_files.buttons_rc

from utils.database_settings import DB_Darsteller, Webside_Settings, ScrapingData, VideoData
from utils.database_settings.database_for_pornbox import PornBoxLinks
from utils.web_scapings.datenbank_scene_maske import DatenbankSceneMaske
from gui.context_menus.context_menu_for_buttons import CustomMenuButtons
from utils.web_scapings.scape_iafd import ScrapeIAFDScene
from utils.web_scapings.scrape_data18 import ScrapeData18
from utils.web_scapings.theporndb.scrape_scene_the_porn_db import ScrapeThePornDBScene
from utils.web_scapings.iafd_performer_link import IAFDInfos
from utils.web_scapings.performer_infos_maske import PerformerInfosMaske
from utils.threads import FileTransferThread, ExifSaveThread
from utils.web_scapings.theporndb.scrape_scene_the_porn_db import ScrapeThePornDBScene
from utils.database_settings.search_title_from_db import SearchTitle
from utils.helpers.umwandeln import from_classname_to_import, count_days
from gui.helpers.message_show import StatusBar, MsgBox, status_fehler_ausgabe, blink_label
from gui.dialoge_ui.einstellungen import Einstellungen
from gui.dialoge_ui.dialog_daten_auswahl import Dlg_Daten_Auswahl
from gui.dialog_nations_auswahl import NationsAuswahl
from gui.context_menu import ContextMenu
from gui.show_performer_images import ShowPerformerImages
from gui.clearing_widgets import ClearingWidget
from gui.dialog_gender_auswahl import GenderAuswahl
from gui.dialog_social_media_auswahl import SocialMediaAuswahl
from gui.dialog_socialmedia_link import SocialMediaLink
from gui.copy_datas_in_gui import CopyDatasInGui

from config import EXIFTOOLPFAD
from config import BUTTONSNAMES_JSON_PATH, PROCESS_JSON_PATH, MEDIA_JSON_PATH, DATENBANK_JSON_PATH
from config import MAIN_UI, BUTTONS_WEBSIDES_UI, TRANSFER_UI
          
### -------------------------------------------------------------------- ###StatusBar
### --------------------- HauptFenster --------------------------------- ###
### -------------------------------------------------------------------- ###
class Haupt_Fenster(QMainWindow):       
    def __init__(self, parent=None):
        super(Haupt_Fenster,self).__init__(parent)        
        uic.loadUi(MAIN_UI,self)
        self.showMaximized()
        self.tabs.setCurrentIndex(0) 
        self.previous_text: dict={}
        self.lnEdit_DBIAFD_artistLink_old: str=""
        self.lnEdit_IAFD_artistAlias_old: str=""
                
        self.tab_changed_handler(3)
        if Path(DATENBANK_JSON_PATH).exists():            
            Path(DATENBANK_JSON_PATH).unlink()          
        self.model_database_weblinks = QStandardItemModel()
        self.lstView_database_weblinks.setModel(self.model_database_weblinks)        
        
        #### -----------  setze Sichtbarkeit auf "False" ----------- #####
        clearing_widget = ClearingWidget(self)         
        clearing_widget.invisible_movie_btn_anzahl()
        clearing_widget.invisible_database_link()
        clearing_widget.invisible_performer_btn_anzahl()
        clearing_widget.invisible_any_labels()
        clearing_widget.clear_social_media_in_buttons()        
        datenbank_performers = DB_Darsteller(self)
        self.cBox_performer_rasse.addItems(self, "Rasse", self.all_rassen_ger(datenbank_performers), datenbank_performers)        
        self.buttons_connections(clearing_widget)

    def all_rassen_ger(self, datenbank_performers)-> list:
        items=[]  
        for item_text in datenbank_performers.get_all_rassen_ger():
            items.append(item_text) 
        return items       
    
    def buttons_connections(self, clearing_widget): 
        self.show_performers_images = ShowPerformerImages(self)  
    ###-------------------------auf Klicks reagieren--------------------------------------###
        ### --------------------------------------- #####
        ### --- Buttons auf den Haupt Widget ------ #####
        self.Btn_Laden.clicked.connect(self.Infos_ExifToolHolen)
        self.Btn_Speichern.clicked.connect(self.Infos_Speichern)
        self.Btn_Refresh.clicked.connect(self.refresh_table)
        self.Btn_Loeschen.clicked.connect(clearing_widget.tabs_clearing)  
        self.Btn_VideoDatenHolen.clicked.connect(self.videodaten_holen) 
        ### ------------------------------------ #####
        ### --- Buttons auf den Infos Tab ------ #####
        self.Btn_logo_am_infos_tab.clicked.connect(self.Websides_Auswahl)
        self.Btn_AddArtist.clicked.connect(self.AddArtist)
        self.Btn_Linksuche_in_DB.clicked.connect(lambda: SearchTitle(self).linksuche_in_db()) 
        self.Btn_Rechts.clicked.connect(self.AddRechts)
        self.Btn_Links.clicked.connect(self.AddLinks)
        self.Btn_copy_runtime.clicked.connect(lambda: CopyDatasInGui(self).copy_runtime_set_in_moviedb())       
        ### ------------------------------------- ####
        ### --- Buttons auf den Analyse Tab ---- #####
        self.Btn_logo_am_analyse_tab.clicked.connect(self.Websides_Auswahl)
        self.Btn_titel_suche.clicked.connect(lambda: SearchTitle(self).search_title())
        self.Btn_name_suche.clicked.connect(lambda: SearchTitle(self).performer_suche())
        self.cBox_performers.currentIndexChanged.connect(self.show_performers_images.show_performer_picture)
        self.Btn_next.clicked.connect(self.show_performers_images.show_next_picture_in_label)
        self.Btn_prev.clicked.connect(self.show_performers_images.show_previous_picture_in_label)
        ### -------------------------------------- #####
        ### --- Buttons auf den Datenbank Tab ---- ##### 
        self.Btn_logo_am_db_tab.clicked.connect(self.Websides_Auswahl)        
        self.Btn_Linksuche_in_Data18.clicked.connect(self.webscrap_data18)
        self.Btn_Linksuche_in_TPDB.clicked.connect(self.webscrap_tpdb)
        self.Btn_Linksuche_in_IAFD.clicked.connect(self.webscrap_iafd)
        self.Btn_AddLink.clicked.connect(self.addLink)
        self.Btn_delLink.clicked.connect(self.delete_link_from_listview)
        self.Btn_AddPerformer.clicked.connect(self.add_performers)
        self.Btn_delPerformer.clicked.connect(self.del_performers) 
        self.Btn_DBUpdate.clicked.connect(self.single_DBupdate)
        self.Btn_addDatei.clicked.connect(self.add_db_in_datei)
        self.Btn_pornbox_links.clicked.connect(self.add_all_pornbox_links)
        self.Btn_copy_dbdata18.clicked.connect(lambda: CopyDatasInGui(self).data18Link_update())
        self.Btn_copy_dbtheporndb.clicked.connect(lambda: CopyDatasInGui(self).ThePornDBLink_update())
        self.Btn_copy_dbiafd.clicked.connect(lambda: CopyDatasInGui(self).IAFDLink_update())
        self.Btn_Clipboard.clicked.connect(lambda: CopyDatasInGui(self).copy_text_to_clipboard())
        ### ---------- Button auf den datenbank Tab per for Loop ----------- ####
        felder = ["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Movies", "Synopsis", "Tags"]                                          
        for feld in felder:            
            button_widget = self.findChild(QPushButton, f'Btn_Anzahl_DB{feld}')
            Line_edit_widget = self.findChild(QLineEdit, f'lnEdit_DB{feld}')
            text_edit_widget = self.findChild(QTextEdit, f'txtEdit_DB{feld}')
            if button_widget:
                button_widget.clicked.connect(self.dialog_auswahl)
        ### ----------- ContextMenu aufrufen in den datenbank Masken --------- ####
            if Line_edit_widget or text_edit_widget:
                widget_obj = Line_edit_widget or text_edit_widget  
                widget_obj.customContextMenuRequested.connect(lambda pos, widget_obj=widget_obj: self.showContextMenu(pos, widget_obj))
        ### ----------------------------------------- #####
        ### ---------- Button auf den Stacked ------- #####
        self.Btn_IAFD_linkmaker.clicked.connect(self.link_maker)
        self.Btn_DateiLaden.clicked.connect(self.Info_Datei_Laden)
        self.Btn_get_last_side.clicked.connect(self.gui_last_side) 
        self.Btn_start_spider.clicked.connect(self.start_spider)  
        self.Btn_RadioBtn_rename.clicked.connect(self.file_rename_from_infos) 
        self.Btn_Titelsuche_in_DB.clicked.connect(lambda: SearchTitle(self).search_title())
        self.Btn_perfomsuche_in_DB.clicked.connect(lambda: SearchTitle(self).performer_suche_in_scene())          
        self.rdBtn_rename.clicked.connect(self.radioBtn_file_rename)         
        self.actionEinstellungen.triggered.connect(lambda :Einstellungen(self).show())
        self.tblWdg_daten.horizontalHeader().sectionClicked.connect(lambda index: self.tblWdg_daten.setSortingEnabled(not self.tblWdg_daten.isSortingEnabled()))
        self.tblWdg_daten.itemClicked.connect(self.show_database_for_movies)
        self.tblWdg_performer.horizontalHeader().sectionClicked.connect(lambda index: self.tblWdg_performer.setSortingEnabled(not self.tblWdg_performer.isSortingEnabled()))
        self.tblWdg_performer.itemClicked.connect(self.show_database_for_performers)
        self.tblWdg_files.itemClicked.connect(self.Ordner_Infos)        
        self.tblWdg_files.horizontalHeader().sectionClicked.connect(lambda index: self.tblWdg_files.setSortingEnabled(not self.tblWdg_files.isSortingEnabled()))        
        self.tblWdg_files.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # onlyRead Table
        ### --- Context Menus ---------------------- ### 
        self.tblWdg_files.customContextMenuRequested.connect(lambda pos, widget_obj=self.tblWdg_files: self.showContextMenu(pos, widget_obj))
        self.tblWdg_performer.customContextMenuRequested.connect(lambda pos, widget_obj=self.tblWdg_performer: self.showContextMenu(pos, widget_obj))      
        self.tblWdg_performer_links.customContextMenuRequested.connect(lambda pos, widget_obj=self.tblWdg_performer_links: self.showContextMenu(pos, widget_obj))
        self.tblWdg_DB_performers.customContextMenuRequested.connect(lambda pos, widget_obj=self.tblWdg_DB_performers: self.showContextMenu(pos, widget_obj))
        clearing_widget.set_website_bio_enabled(self.get_bio_websites(widget=True), False)
        self.set_website_bio_context_menu()
        ### ------------ Text/Tab Wechsel Reaktion ------------------ ###
        self.lnEdit_URL.textChanged.connect(lambda index: self.Btn_Linksuche_in_DB.setEnabled(bool(self.lnEdit_URL.text().startswith("https://"))))
        self.tabs.currentChanged.connect(self.tab_changed_handler)
        self.lnEdit_DBIAFDLink.textChanged.connect(self.Web_IAFD_change)
        self.lnEdit_DBData18Link.textChanged.connect(self.Web_Data18_change)
        self.lnEdit_DBThePornDBLink.textChanged.connect(self.Web_ThePornDB_change)              
        self.lnEdit_URL.textChanged.connect(self.link_isin_from_db)
        self.lnEdit_db_titel.textChanged.connect(self.titelsuche_in_DB_aktiv)
        self.lnEdit_db_performer.textChanged.connect(self.performersuche_in_DB_aktiv)
        self.cBox_studio_links.currentIndexChanged.connect(lambda index :self.Btn_start_spider.setEnabled(bool(self.cBox_studio_links.currentText()))) 
        ### ---------------- Performer Tab --------------------------- ###
        self.lnEdit_DBIAFD_artistLink.textChanged.connect(self.Web_IAFD_artist_change)         
        self.Btn_IAFD_perfomer_suche.clicked.connect(self.get_IAFD_performer_link)
        self.Btn_Linksuche_in_IAFD_artist.clicked.connect(self.load_IAFD_performer_link)
        self.Btn_performers_gender.clicked.connect(lambda :GenderAuswahl(self).exec())
        self.Btn_DB_perfomer_suche.clicked.connect(self.datenbank_performer_suche) 
        self.customlnEdit_IAFD_performer.returnPressed.connect(self.datenbank_performer_suche)       
        self.Btn_DBArtist_Update.clicked.connect(self.update_datensatz)
        self.Btn_table_links_expanding.clicked.connect(self.expand_table_performer_links)
        self.Btn_table_daten_expanding.clicked.connect(self.expand_table)
        self.Btn_seiten_vor.clicked.connect(self.datenbank_performer_suche_nextpage)
        self.Btn_seiten_zurueck.clicked.connect(self.datenbank_performer_suche_prevpage)
        self.lnEdit_page.returnPressed.connect(self.datenbank_performer_suche_gopage)
        self.tblWdg_performer_links.clicked.connect(self.show_performers_images.show_performer_picture)
        self.Btn_performer_next.clicked.connect(self.show_performers_images.show_next_picture_in_label)
        self.Btn_performer_prev.clicked.connect(self.show_performers_images.show_previous_picture_in_label)
        self.Btn_DB_perfomer_table_update.clicked.connect(self.performer_tab_update_tabelle)
        self.Btn_iafd_link_copy.clicked.connect(self.copy_clipboard_iafdlink)
        self.chkBox_iafd_enabled.stateChanged.connect(self.toggle_iafd_performer_state)
        self.lnEdit_IAFD_artistAlias.doubleClicked.connect(self.take_iafdname_in_name)
        self.Btn_delete_logs.clicked.connect(lambda :self.txtBrowser_loginfos.clear())
        self.cBox_performer_rasse.update_buttonChanged.connect(lambda enabled: self.Btn_DBArtist_Update.setEnabled(enabled))
        self.Btn_nations_edititem.clicked.connect(lambda :NationsAuswahl(parent=self).exec())
        self.Btn_social_media_edititem.clicked.connect(lambda :SocialMediaAuswahl(parent=self, items_dict=self.get_social_media_dict()).exec())        
         
        for widget in self.get_bio_websites(widget=True):  # wenn bio_websites änderungen sind, dann Update aktiv
            btn = getattr(self, f"Btn_performer_in_{widget}")
            btn.tooltipChanged.connect(self.check_avaible_bio_websites) 
        
        widgets = clearing_widget.performers_tab_widgets("lineprefix_perf_textprefix_perf_lineiafd")
        for widget in widgets:
            if widget not in ["lnEdit_DBIAFD_artistLink"]:
                getattr(self, widget).textChanged.connect(partial(self.performer_text_change, widget=widget, color_hex='#FFFD00'))    
        ###-----------------------------------------------------------------------------------###
        for i in range(1,6):            
            stacked_widget = self.findChild(QPushButton, f'Btn_stacked_next_{i}')  
            stacked_widget.clicked.connect(lambda: self.stackedWidget.setCurrentIndex((self.stackedWidget.currentIndex() + 1) % self.stackedWidget.count()))
        for i in range(1,3):
            stacked_widget = self.findChild(QPushButton, f'Btn_stacked_webdb_next_{i}')  
            stacked_widget.clicked.connect(lambda: self.stacked_webdb_images.setCurrentIndex((self.stacked_webdb_images.currentIndex() + 1) % self.stacked_webdb_images.count()))
        for i in range(1,3):
            stacked_widget = self.findChild(QPushButton, f'Btn_stacked_info_next_{i}')  
            stacked_widget.clicked.connect(lambda: self.stacked_image_infos.setCurrentIndex((self.stacked_image_infos.currentIndex() + 1) % self.stacked_image_infos.count()))
    
    def get_bio_websites(self, widget=False, url=False) -> list:
        widgets_urls ={"BabePedia": "https://www.babepedia.com/", 
                     "theporndb": "https://api.theporndb.net",
                     "indexxx": "https://www.indexxx.com/",
                     "TheNude": "https://www.thenude.com/",
                     "Freeones": "https://www.freeones.com/" }        
        if widget:
            return list(widgets_urls.keys())
        if url:
            return list(widgets_urls.values())
        return widgets_urls

    def check_avaible_bio_websites(self):
        button = self.sender() 
        for name, url in self.get_bio_websites().items(): 
            if button.toolTip().startswith(url):
                button_name= button.objectName().replace("Btn_performer_in_", "")
                ClearingWidget(self).set_website_bio_enabled([button_name],True)
                self.Btn_DBArtist_Update.setEnabled(True)

    def toggle_iafd_performer_state(self, is_checked):        
        is_change=False
        # Überprüfen, ob der veränderungen ist und die Farbe entsprechend setzen
        if self.lnEdit_DBIAFD_artistLink_old != self.lnEdit_DBIAFD_artistLink.text() and self.lnEdit_DBIAFD_artistLink.text() != "N/A":
            is_change=True
            self.lnEdit_DBIAFD_artistLink_old = self.lnEdit_DBIAFD_artistLink.text()
            self.lnEdit_IAFD_artistAlias_old = self.lnEdit_IAFD_artistAlias.text()
        self.set_default_color("lnEdit_DBIAFD_artistLink")
        color_hex = '#FFFD00' if is_change or not is_checked else '#FFFDD5' 

        self.set_color_stylesheet("lnEdit_DBIAFD_artistLink", color_hex=color_hex)
        self.set_color_stylesheet("lnEdit_IAFD_artistAlias", color_hex=color_hex)  

        self.lnEdit_DBIAFD_artistLink.setText(self.lnEdit_DBIAFD_artistLink_old if is_checked else "N/A")
        self.lnEdit_IAFD_artistAlias.setText(self.lnEdit_IAFD_artistAlias_old if is_checked else "")

        self.lnEdit_DBIAFD_artistLink.setEnabled(is_checked)
        self.lnEdit_IAFD_artistAlias.setEnabled(is_checked)

    def take_iafdname_in_name(self):
        if self.lnEdit_IAFD_artistAlias.text():
            self.lnEdit_performer_info.setText(self.lnEdit_IAFD_artistAlias.text())
            self.lnEdit_performer_ordner.setText(self.lnEdit_IAFD_artistAlias.text())
            blink_label(self,"lnEdit_performer_info","#74DF00")
            blink_label(self,"lnEdit_performer_ordner","#74DF00")
        else:
            StatusBar(self, "IAFD Alias Text Feld ist leer !", "#FF0000")

    def set_performer_maske_text_connect(self, disconnect=False):
        clearing_widget = ClearingWidget(self)
        widgets = clearing_widget.performers_tab_widgets("lineprefix_perf_textprefix_perf_lineiafd")
        for widget in widgets:
            getattr(self, widget).blockSignals(disconnect)     

    def performer_text_change(self, widget, color_hex='#FFFDD5'):        
        if color_hex=='#FFFD00':
            self.Btn_DBArtist_Update.setEnabled(True)
        new_text = getattr(self, widget).toPlainText() if isinstance(getattr(self, widget), QTextEdit) else getattr(self, widget).text()           
        if new_text != self.previous_text.get(widget, ""):
            self.previous_text[widget] = new_text 
            color_hex = '#FFFD00' if new_text !="" else '#FFFDD5'
            self.set_color_stylesheet(widget, color_hex)  

    def set_color_stylesheet(self, widget, color_hex='#FFFDD5'):
        current_style = getattr(self, widget).styleSheet()
        current_style = current_style.replace("#FFFDD5", color_hex)
        current_style = current_style.replace("#FFFD00", color_hex)
        getattr(self, widget).setStyleSheet(current_style)  

    def set_default_color(self, widget):
        default_style="QLineEdit,QTextEdit {background-color: #FFFDD5;} \
                    QLineEdit:hover,QTextEdit:hover {border: 2px solid rgb(49, 50, 62);} \
                    QLineEdit:focus,QTextEdit:focus {border: 2px inset rgb(85, 170, 255);} \
                    QLineEdit::placeholderText {color: #FFFDD5;}"
        getattr(self, widget).setStyleSheet(default_style) 

    def tab_changed_handler(self, index: int) -> None:
        if index == 0:
            self.tblWdg_daten.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.stacked_tables.setCurrentWidget(self.stacked_page_table_files) 
            self.stackedWidget.setCurrentWidget(self.stacked_active_file)

        if index == 1:
            self.tblWdg_daten.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.stacked_tables.setCurrentWidget(self.stacked_page_table_daten)             
            self.stackedWidget.setCurrentWidget(self.stacked_db_abfrage)           
            self.set_analyse_daten()

        if index ==2: 
            self.tblWdg_daten.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
            self.stacked_tables.setCurrentWidget(self.stacked_page_table_daten)           
            self.stackedWidget.setCurrentWidget(self.stacked_IAFD_Linkmaker) 
            header_labels = SearchTitle(self).get_header_for_movie_table()
            self.tblWdg_daten.setColumnCount(len(header_labels))
            self.tblWdg_daten.setHorizontalHeaderLabels(header_labels)          
            links = self.lstView_database_weblinks.model().data(self.lstView_database_weblinks.model().index(0, 0))
            if links:
                self.set_studio_in_db_tab(links)

        if index ==3:
            self.tblWdg_performer.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.stacked_tables.setCurrentWidget(self.stacked_page_table_performer)         
            self.stackedWidget.setCurrentWidget(self.stacked_IAFD_artist)
            self.stacked_image_infos.setCurrentWidget(self.perfomer_image)
            header_labels=self.get_header_for_performers_table()            
            self.tblWdg_performer.setColumnCount(len(header_labels))
            self.tblWdg_performer.setHorizontalHeaderLabels(header_labels)
            self.tblWdg_performer_links.setColumnWidth(4, 20)

    def set_studio_in_db_tab(self, link):
        baselink = urlparse(link).netloc
        scraping_data = ScrapingData(MainWindow=self)        
        studio_name = scraping_data.from_link_to_studio(baselink)
        self.set_button_from_studioname(studio_name)
    
    def set_button_from_studioname(self, studio_name):
        db_webside_settings = Webside_Settings(MainWindow=self)
        errorview, studio, logo = db_webside_settings.get_buttonlogo_from_studio(studio_name)  
        if errorview:
            logo="background-image: url(':/Buttons/_buttons/no-logo_90x40.jpg')"
            studio="kein Studio ausgewählt !"
        self.set_database_tab_enabled(logo, studio)

    def showContextMenu(self, pos: int, widget_name):        
        current_widget = self.sender()
        if current_widget:
            context_menu = ContextMenu(self)
            context_menu.showContextMenu(current_widget.mapToGlobal(pos), widget_name)   

    def set_website_bio_context_menu(self) -> None:
        for widget in self.get_bio_websites(widget=True):
            bio_button = getattr(self, f"Btn_performer_in_{widget}")
            bio_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            bio_button.customContextMenuRequested.connect(self.show_context_menu)         

    def show_context_menu(self, pos):
        current_widget = self.sender()        
        menu = CustomMenuButtons(self)
        menu.show_context_menu(current_widget, current_widget.mapToGlobal(pos)) 
    
    def refresh_table(self, new_file: str=None) -> None: 
        sort = self.tblWdg_files.isSortingEnabled()          
        self.tblWdg_files.hide()
        self.Info_Datei_Laden(refresh=True)
        QTimer.singleShot(300, lambda :self.tblWdg_files.show())
        self.tblWdg_files.setSortingEnabled(sort)         
        if new_file:            
            self.activate_item(new_file)
        elif self.tblWdg_files.selectedItems():
            self.activate_item(self.tblWdg_files.selectedItems()[0].text())       
           

    def activate_item(self, gesuchter_text):
        for row in range(self.tblWdg_files.rowCount()):
            item = self.tblWdg_files.item(row, 0)  # Hier 0 für die erste Spalte, ändere es entsprechend
            if item and item.text() == gesuchter_text:
                item.setSelected(True)
                item_pos = self.tblWdg_files.visualItemRect(item).center()
                QTest.mouseClick(self.tblWdg_files, Qt.MouseButton.LeftButton, pos=item_pos)
                break                

    def add_current_text_to_combobox(self):
        current_text = self.cBox_performer_fanside.currentText()        
        if current_text:  # Füge nur hinzu, wenn der Text nicht leer ist
            self.cBox_performer_fanside.addItem(current_text)
 

    def titelsuche_in_DB_aktiv(self):
        if self.Btn_logo_am_db_tab.toolTip() != "kein Studio ausgewählt !":            
            self.Btn_Titelsuche_in_DB.setEnabled(True)

    def performersuche_in_DB_aktiv(self):
        if self.Btn_logo_am_db_tab.toolTip() != "kein Studio ausgewählt !":
            self.Btn_perfomsuche_in_DB.setEnabled(True)
        
    ### --------------------------------------------------------------------- ###
    def radioBtn_file_rename(self):
        if self.tblWdg_files.rowCount() == 0 or self.lnEdit_Studio.text() == "":
            zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
            StatusBar(self, f"{zeit}: Die Tabelle oder das PornSide Label ist leer ! Umbennen nicht möglich !","#ff3000")            
            self.rdBtn_rename.setChecked(False) 
            self.Btn_RadioBtn_rename.setEnabled(False)           
        else:
            self.Btn_RadioBtn_rename.setEnabled(not self.Btn_RadioBtn_rename.isEnabled())
        
    def datenbank_save(self,info_art: str, source: str=None, daten: str=None) -> None:
        if info_art == "delete":
        # Lösche die JSON-Datei und beende die Funktion
            if Path(DATENBANK_JSON_PATH).exists():
                Path(DATENBANK_JSON_PATH).unlink()
                clearing = ClearingWidget(self)
                clearing.invisible_movie_btn_anzahl()
                clearing.loesche_DB_maske()
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
        print(self.lnEdit_Studio.text())
        errorview, verschiebe_ordner = db_webside_settings.hole_verschiebe_ordner(self.lnEdit_Studio.text())
        move_file = self.tblWdg_files.selectedItems()[0].text()+".mp4" 
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
        self.Transfer.lbl_Dest_Folder.setStyleSheet("background-color: none;font: none;")
        self.Transfer.label_gif_transfer.setVisible(True)        
        self.movie = QMovie(":/labels/_dialog_label/transfer.gif")        
        if Path(verschiebe_ordner).exists(): 
            self.Transfer.label_gif_transfer.setMovie(self.movie)   
            self.startTransfer(directory +"/"+ move_file,verschiebe_ordner +"/"+ move_file)            
            self.movie.start()
        else:
            self.Transfer.label_gif_transfer.setPixmap(QPixmap(":/labels/_dialog_label/sign-error-icon.png"))
            self.Transfer.lbl_Dest_Folder.setStyleSheet("background-color: #ff3000")
            self.Transfer.lbl_Dest_Folder.setText(f"Ordner '{verschiebe_ordner}' nicht vorhanden !") 
            self.Transfer.btn_OK_transfer.clicked.connect(self.Transfer.close)

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
        self.Transfer.label_gif_transfer.setPixmap(QPixmap(":/labels/_dialog_label/sign-error-icon.png"))      
        Path(self.transferThread.target_path).unlink()
        minutes, seconds = divmod(remaining_time, 60) 
        self.Transfer.lbl_speed.setText(f"{avg_speed:.2f} MB/s - geschätzte Zeit bis zum Ende: {minutes:02d}:{seconds:02d}s > ABBRUCH !!!")
        
    def transferFinished(self): 
        self.Transfer.btn_OK_transfer.setEnabled(True)
        self.Transfer.btn_OK_transfer.raise_() 
        self.transferThread.quit()
        self.transferThread.wait()
        self.movie.stop()
        self.Transfer.label_gif_transfer.setPixmap(QPixmap(":/labels/_dialog_label/Info.jpg"))
        self.Transfer.lbl_speed.setText("100 MB/s - geschätzte Zeit bis zum Ende: 00:00s > FERTIG !!!")        
        if (Path(self.transferThread.source_path).stat().st_size == Path(self.transferThread.target_path).stat().st_size
           and self.transferThread.source_path!=self.transferThread.target_path):
            Path(self.transferThread.source_path).unlink()
            row_index = self.tblWdg_DB_performers.currentRow()
            self.tblWdg_files.removeRow(row_index)  
        self.Transfer.btn_OK_transfer.clicked.connect(lambda: self.ordner_transfer_zurueck(False, self.transferThread.target_path))          

    # IAFD Link Maker
    def IAFDLink(self):
        infos_webside = DatenbankSceneMaske(MainWindow=self)
        titel = self.lnEdit_Titel.text()
        jahr = self.lnEdit_Jahr.text()
        infos_webside.IAFDLink(titel,jahr)
    
    def dialog_auswahl(self):
    # Erstellen Sie eine Instanz des Dlg_Daten_Auswahl-Dialogs
        dlg = Dlg_Daten_Auswahl(MainWindow=self)
        # Rufen Sie die exec-Methode auf, um das Dialogfenster anzuzeigen
        dlg.exec()  
            


    def update_page_and_search(self, new_page):
        if self.customlnEdit_IAFD_performer.text() != "":
            page_max = int(self.lnEdit_maxpage.text())
            page = new_page
            if page < 1:
                page = page_max
            elif page > page_max:
                page = 1
            self.lnEdit_page.setText(f"{page}")
            self.datenbank_performer_suche()
        else:
            QTimer.singleShot(100, lambda: self.customlnEdit_IAFD_performer.setStyleSheet('background-color: #FF0000'))
            QTimer.singleShot(3500, lambda: self.customlnEdit_IAFD_performer.setStyleSheet('background-color:'))

    def datenbank_performer_suche_prevpage(self):
        self.update_page_and_search(int(self.lnEdit_page.text()) - 1)

    def datenbank_performer_suche_gopage(self):
        self.update_page_and_search(int(self.lnEdit_page.text()))

    def datenbank_performer_suche_nextpage(self):
        self.update_page_and_search(int(self.lnEdit_page.text()) + 1)

    def datenbank_performer_suche(self):        
        if self.sender() in [self.Btn_DB_perfomer_suche, self.customlnEdit_IAFD_performer]:
            self.tblWdg_performer.raise_()
            self.tabs.setCurrentWidget(self.tab_performer) 
            self.tblWdg_performer.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customlnEdit_IAFD_performer.addToHistory(self.customlnEdit_IAFD_performer.text())            
            self.lnEdit_page.setText("1")
            self.lnEdit_maxpage.setText("1")
            self.show_performers_images = ShowPerformerImages(self)        
        clearing=ClearingWidget(MainWindow=self)
        clearing.clear_maske()
        artist=self.customlnEdit_IAFD_performer.text()        
        if len(artist) > 1:
            if artist.endswith("*"):
                artist = f"{artist[:-1]}%"
            if artist.startswith("*"):
                artist = f"%{artist[1:]}"
        elif artist == "*":
            artist = "%"

        page_number=int(self.lnEdit_page.text())
        db_for_darsteller = DB_Darsteller(MainWindow=self)
        artist_data = db_for_darsteller.get_all_datas_from_database(artist, page_number)
        if artist_data == f"kein {artist} gefunden":
            self.tblWdg_performer.setRowCount(0)            
            self.customlnEdit_IAFD_performer.setStyleSheet('background-color: #FF0000')          
            QTimer.singleShot(500, lambda :self.customlnEdit_IAFD_performer.setStyleSheet('background-color:'))
            QTimer.singleShot(1000, lambda :self.customlnEdit_IAFD_performer.setStyleSheet('background-color: #FF0000'))
            QTimer.singleShot(2500, lambda :self.customlnEdit_IAFD_performer.setStyleSheet('background-color: '))
        else:
            self.tabelle_erstellen_fuer_performer()
    
    def update_datensatz(self):
        performer_infos_maske = PerformerInfosMaske(MainWindow=self)
        performer_infos_maske.update_datensatz()

    def expand_table_performer_links(self):
        table_widget_breite=self.tblWdg_performer_links.height()
        if table_widget_breite == 140:
            self.tblWdg_performer_links.setGeometry(30, 360, 870, 140+300)
            self.Btn_table_links_expanding.move(450, 505+300)
        else:
            self.tblWdg_performer_links.setGeometry(30, 360, 870, 140)
            self.Btn_table_links_expanding.move(450, 505)

    def expand_table(self):
        tables = ["files", "performer", "daten"]
        current_page = self.stacked_tables.currentWidget()
        for table in tables:            
            widget_table = current_page.findChild(QTableWidget, f"tblWdg_{table}")
            if widget_table:                
                break
        table_widget_laenge=widget_table.width()
        if table_widget_laenge == 890:
            expand=970
            self.stacked_tables.setGeometry(30, 210, 890 + expand, 750)
            widget_table.setGeometry(0, 0, 890 + expand, 750) 
            self.Btn_table_daten_expanding.move(925 + expand, 540)  # Button move nach ganz rechts
        else:
            self.stacked_tables.setGeometry(30, 210, 890, 750)
            widget_table.setGeometry(0, 0, 890, 750)
            self.Btn_table_daten_expanding.move(925, 540)
    


    ### ------------------------ Performer Tabelle ----------------------- ###
    def get_header_for_performers_table(self):
        return ["ArtistID", "Name", "Ordner", "IAFDLink", "BabePedia", "Geschlecht", "Rassen", "Nation", "Geburtstag", "Birth_Place", 
                "OnlyFans", "Boobs","Gewicht", "Groesse","Bodytyp", "Piercing","Tattoo","Haarfarbe", "Augenfarbe","Aktiv"]

    def tabelle_erstellen_fuer_performer(self): 
        self.stacked_tables.setCurrentWidget(self.stacked_page_table_performer)        
        artist_data_json=VideoData().load_from_json()
        header_labels=self.get_header_for_performers_table()
        self.tblWdg_performer.setColumnCount(len(header_labels))
        self.tblWdg_performer.setHorizontalHeaderLabels(header_labels)
        for row, artist_data in enumerate(artist_data_json):            
            self.tblWdg_performer.setRowCount(row+1)
            for column, db_feld_name in enumerate(header_labels): 
                self.tblWdg_performer.setItem(row,column,QTableWidgetItem(f'{artist_data[db_feld_name]}'))  
        self.tblWdg_performer.setCurrentCell(row, 0)  
   
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
        return(studio, file_name, sorted(name_all))
    
    def copy_clipboard_iafdlink(self):
        pyperclip.copy(self.lnEdit_DBIAFD_artistLink.text())
        self.widget_animation("lnEdit_DBIAFD_artistLink")

    def widget_animation(self, widget):
        self.animation = QVariantAnimation()
        self.animation.setEndValue(QColor(255, 250, 211)) # rgb(255, 250, 211)
        self.animation.setStartValue(QColor(58, 223, 0)) #  rgb(58, 223, 0)
        self.animation.setDuration(1000)
        self.animation.valueChanged.connect(lambda :self.animate(widget))
        self.animation.start()
        
    def animate(self, widget):
        color = self.animation.currentValue()
        getattr(self,widget).setStyleSheet("background-color: %s;" % color.name())
    
    ### ------------------------------------------------------------------------------------ ###
    ### ---- vom Basislink incl IAFD Link, gucken ob es da schon einn Eintrag für gibt ----- ###
    ### ------------------------------------------------------------------------------------ ###
    def link_isin_from_db(self): 
        link = self.lnEdit_URL.text()                 
        base_url = self.get_baselink(link)
        iafdlink = link if link.startswith("https://www.iafd.com/") else None
        scraping_data  = ScrapingData(MainWindow=self)
        if base_url or iafdlink:
            link_in_db = scraping_data.is_link_in_db(base_url, iafdlink) # schaut ob weblink oder iafdlink da is 
        self.Btn_addDatei.setEnabled(link_in_db)            

    def get_baselink(self, url):
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        base_url = parsed_url.netloc
        return scheme + "://" + base_url
    
    def link_maker(self):
        if self.lnEdit_IAFD_titel.text()!="" and self.lnEdit_db_jahr.text()!="":            
            self.link_maker_iafd()
        elif self.lnEdit_DBTitel.text()!="" and self.lnEdit_DBRelease.text()!="":
            self.lnEdit_IAFD_titel.setText(self.set_iafd_conform(self.lnEdit_DBTitel.text()))
            self.lnEdit_db_jahr.setText(self.lnEdit_DBRelease.text()[:4])
            self.link_maker_iafd()
        else:
            MsgBox(self, "Bitte Titel und Jahr angeben","w")
    
    def set_iafd_conform(self, title):
        change_letters_dict = {"The ": "", 
                               "A ": "",
                               " & ": " and ",
                               "?": "",
                               "!": ""}
        for key, value in change_letters_dict.items():
            title = title.replace(key, value)         
        return title

    def link_maker_iafd(self):
        title=self.lnEdit_IAFD_titel.text().lower().replace(" ","+")            
        hostname=f'https://www.iafd.com/title.rme/title={title}/year={self.lnEdit_db_jahr.text()[:4]}/{title.replace("+","-")}.htm'
        pyperclip.copy(hostname)
        self.txtEdit_Clipboard.setPlainText(f"IAFD Link: \n{hostname}")

    def Web_IAFD_change(self):        
        scrape_iafd_scene = ScrapeIAFDScene(MainWindow=self)
        scrape_iafd_scene.Web_IAFD_change() 

    def Web_IAFD_artist_change(self):
        if self.chkBox_iafd_enabled.isChecked():            
            self.performer_text_change("lnEdit_DBIAFD_artistLink", color_hex='#FFFD00')        
            iafd_infos = IAFDInfos(MainWindow=self)
            iafd_infos.check_IAFD_performer_link()         

    def performer_tab_update_tabelle(self):
        performer_infos_maske = PerformerInfosMaske(MainWindow=self)
        performer_infos_maske.update_tabelle()                                

    def get_IAFD_performer_link(self): 
        iafd_infos = IAFDInfos(MainWindow=self)
        iafd_infos.get_IAFD_performer_link()  

    def load_IAFD_performer_link(self): 
        iafd_infos = IAFDInfos(MainWindow=self)
        iafd_link=self.lnEdit_DBIAFD_artistLink.text()
        id = self.grpBox_performer_name.title().replace("Performer-Info ID: ","")
        name = self.lnEdit_performer_info.text()
        iafd_infos.load_IAFD_performer_link(iafd_link, id, name) 
        PerformerInfosMaske(self).set_iafd_infos_in_ui()       

    def Web_Data18_change(self):
        scrape_data18_scene = ScrapeData18(MainWindow=self)
        scrape_data18_scene.Web_Data18_change() 

    def Web_ThePornDB_change(self):
        scrape_theporndb_scene = ScrapeThePornDBScene(MainWindow=self)
        #infos_webside.Web_Data18_change() 

    def webscrap_data18(self):        
        self.lbl_checkWeb_Data18URL.setVisible(True)
        scrape_data18_scene = ScrapeData18(MainWindow=self)
        scrape_data18_scene.webscrap_data18()  
    
    def webscrap_tpdb(self):
        self.lbl_checkWeb_ThePornDBURL.setVisible(True)
        scrape_theporndb_scene = ScrapeThePornDBScene(MainWindow=self)
        scrape_theporndb_scene.webscrap_scene()

    def webscrap_iafd(self):
        self.lbl_checkWeb_IAFDURL.setVisible(True)
        scrape_iafd_scene = ScrapeIAFDScene(MainWindow=self)
        scrape_iafd_scene.webscrap_iafd()

    def webscrap_theporndb(self):
        self.lbl_checkWeb_ThePornDBURL.setVisible(True)
        scrape_theporndb_scene = ScrapeThePornDBScene(MainWindow=self)
        scrape_theporndb_scene.webscrap_scene()

    def videodaten_holen(self):
        self.stackedWidget.setCurrentWidget(self.stacked_web_scan)
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

    ### --------------- Social Media Button -------------------- ###
    def set_social_media_in_buttons(self, social_medias):  
        socialmedias = self.get_social_media_dict()
        social_media_links = social_medias.split("\n") if social_medias else ""
        for zahl, social_media_link in enumerate(social_media_links): # zahl startet mit 1
            found = False         
            for key, value in socialmedias.items():
                if value in social_media_link:
                    self.set_socialmedia_in_button(social_media_link, value, zahl)
                    found = True
                    break 
            if not found:
                value=self.check_own_website(social_media_link)
                if value:
                    self.set_socialmedia_in_button(social_media_link, value, zahl)
                        
    def get_social_media_dict(self):
        return  {"https://twitter.com": "twitter",
                "https://www.facebook.com/": "facebook",
                "https://www.instagram.com/": "instagram",                
                "https://onlyfans.com/": "onlyfans",
                "https://fancentro.com/": "fancentro",
                "https://linktr.ee/": "linktr.ee",
                "https://www.loyalfans.com/": "loyalfans",
                "https://www.twitch.tv/": "twitch",
                "https://www.manyvids.com/": "manyvids",
                "https://www.youtube.com/": "youtube",
                "https://fansly.com/.com/": "fansly",
                "https://www.snapchat.com/": "snapchat"} 

    def set_socialmedia_in_button(self, social_media_link: str, value: str, zahl: int):
        if zahl <= 9:        
            button = getattr(self,f"Btn_performers_socialmedia_{zahl}")
            button.setProperty("social_media", social_media_link)  
            button.setIcon(QIcon(f":/Buttons/_buttons/socialmedia/{value}-25.png"))
            button.clicked.connect(lambda _, num=zahl: SocialMediaLink(self, button=str(num)).exec())
            button.setToolTip(social_media_link)    
            button.setVisible(True)

    def check_own_website(self, social_media_link: str) -> None:
        name=self.lnEdit_performer_info.text().lower()
        value: str=""
        for namen_parts in name.split(" "):
            value = "www" if namen_parts in social_media_link.lower() else value            
        return value
     ### --------------------------------------------------------------- ###

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

    def datei_datum(self,datum : str) -> str:
        datum=str(datetime.fromtimestamp(datum))
        return datum[:datum.rfind(".")]

    def datei_groesse_in_bytes(self,dir : Path, file_name: Path) -> str:
        file_size=Path(dir / file_name).stat().st_size    
        regex = re.compile("^\d*\D?\d{1,%s}|\d{1,%s}" % (3, 3))
        datei_groesse = ".".join(regex.findall(("%.1f" % file_size)[::-1]))[::-1] 
        return str(datei_groesse)[:-2]+" Bytes"
    
    def get_header_for_files_table(self):
        return ["Dateiname", "Datei-Größe", "Aänderungsdatum", "Typ"]

    def Info_Datei_Laden(self, refresh=False):       
        directory = Path(self.lbl_Ordner.text())
        if not refresh:
            einstellungen_ui = Einstellungen(self)
            directory = einstellungen_ui.get_last_folder()
        if directory and directory.exists() and directory.is_dir(): 
            self.tblWdg_files.setRowCount(0)           
            self.tblWdg_files.clearContents()
            header_labels = self.get_header_for_files_table()  
            self.tblWdg_files.setColumnCount(len(header_labels))
            self.tblWdg_files.setHorizontalHeaderLabels(header_labels)
            self.lbl_Ordner.setText(str(directory))
            supported_extensions = (".mp4", ".avi", ".mkv", ".wmv")
            zeile = 0  # Zeilennummer initialisieren

            for file in directory.iterdir():
                if file.suffix in supported_extensions:
                    datum = file.stat().st_ctime                    
                    file_name = str(file.stem)
                    file_size = self.datei_groesse_in_bytes(directory, file)
                    date_formatted = self.datei_datum(datum)
                    self.tblWdg_files.setRowCount(zeile + 1)
                    self.tblWdg_files.setItem(zeile, 0, QTableWidgetItem(file_name))                    
                    self.tblWdg_files.setItem(zeile, 1, QTableWidgetItem(file_size))                    
                    self.tblWdg_files.setItem(zeile, 2, QTableWidgetItem(date_formatted))
                    self.tblWdg_files.setItem(zeile, 3, QTableWidgetItem(file.suffix[1:]))
                    self.tblWdg_files.item(zeile, 1).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignJustify)
                    self.tblWdg_files.item(zeile, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignJustify)
                    zeile += 1

            self.tblWdg_files.resizeColumnsToContents()
            ClearingWidget(self).tabs_clearing(False, False)
        else:
            if directory:
                MsgBox(self, "Datei ist nicht vorhanden!", "w")
                StatusBar(self, f"Daten: '{directory}' konnte nicht geladen werden !", "#F78181")

    def Ordner_Infos(self) -> None:
        self.tblWdg_files.setCurrentCell(self.tblWdg_files.currentRow(),0)
        try:
            self.lbl_Dateiname.setText(self.tblWdg_files.selectedItems()[0].text()+".mp4")
            self.tabs.setCurrentIndex(0)
            einstellung_ui = Einstellungen(self)
            if einstellung_ui.chkBox_InfosExifTool.isChecked():
                self.Infos_ExifToolHolen()
        except IndexError:
            self.tblWdg_files.clearContents() 

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
            self.set_database_tab_enabled(logo, studio)   

    def set_database_tab_enabled(self, logo, studio) -> None:
        self.Btn_logo_am_db_tab.setStyleSheet(logo)
        self.Btn_logo_am_db_tab.setToolTip(studio) 
        self.Btn_pornbox_links.setVisible(studio == "PornWorld")
        self.Btn_DBUpdate.setEnabled(bool(self.lnEdit_DBTitel.text())) ### wenn "" deaktiv
        self.Btn_addDatei.setEnabled(bool(self.lnEdit_DBTitel.text())) ### wenn !="" aktiv

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
        self.refresh_table(self.lbl_Dateiname.text()[:-4]) 
    
    def windows_file_filter(self, file_name):
        # Definieren Sie einen regulären Ausdruck, um ungültige Zeichen zu finden
        invalid_chars_pattern = r"[^-a-zA-Z0-9_äöü.,()&+#!\[\] ?*]+" # <-- [':', '"', '/', '\\', '|', '?', '*']        
        # Entfernen Sie ungültige Zeichen aus dem Dateinamen
        cleaned_file_name = re.sub(invalid_chars_pattern, '', file_name.strip())
        return cleaned_file_name

    def make_simlink(self,movies,verschiebe_ordner,move_file):
        ziel_symlink=""
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
                ziel_verzeichnis = self.get_ziel_verzeichnis(einsvor_verschiebe_ordner, movie_name)                
                dateiname = f"{scene_nr}{move_file}.lnk"
                symlink_meldung = f'/ Symlink >{dateiname}< erstellt !'
            if ziel_verzeichnis:
                dateiname = self.windows_file_filter(dateiname)
                ziel_symlink = ziel_verzeichnis / dateiname
                ziel_symlink.parent.mkdir(parents=True, exist_ok=True)  # Erstelle Verzeichnis rekursiv
                symlink_meldung = f'/ Symlink >{ziel_symlink}< erstellt !'            

            # Erstelle den Symbolic Link            
            shell = win32com.client.Dispatch("WScript.Shell")
            link = shell.CreateShortcut(f"{ziel_symlink}")
            link.TargetPath = verschiebe_ordner +"\\"+ move_file
            try:
                link.Save()
            except Exception as e:
                symlink_meldung=f"Fehler beim Erstellen des Symlinks: {e}"
            StatusBar(self, f"Datei {move_file} wird in {verschiebe_ordner} verschoben ... Fertig !!{symlink_meldung}","#efffb7")       

    def get_ziel_verzeichnis(self, einsvor_verschiebe_ordner, movie_name):
        ziel_verzeichnis = Path(einsvor_verschiebe_ordner, "_Movies", movie_name.strip())
        if not ziel_verzeichnis.exists():
            try:
                ziel_verzeichnis.mkdir()
            except Exception as e:
                ziel_verzeichnis = None            
        return ziel_verzeichnis
    def AddLinks(self):
        listItems=self.lstWdg_Darsteller.selectedItems()
        if not listItems: return        
        for item in listItems: 
            self.lstWdg_Darstellerin.addItem(item.text())
            self.lstWdg_Darsteller.takeItem(self.lstWdg_Darsteller.row(item))  
  
    def get_actors(self, actor_list: QListWidget, comma: str, gender: str)-> str:
        return comma.join([actor_list.item(item).text() + gender for item in range(actor_list.count())])
    
    def format_actors(self, ampers_and: str, comma: str)-> str: # amper_and = "&"
        female = self.get_actors(self.lstWdg_Darstellerin, comma, "")
        male = self.get_actors(self.lstWdg_Darsteller, comma, "(m)")
        if female and male:
            return f"{female}{ampers_and}{male}"
        else:
            return f"{female}"       

    def Infos_Speichern(self):        
        old_file=self.lbl_Dateiname.text()
        new_file=self.windows_file_filter(self.lbl_Dateiname.text())
        process_output={"stdout": "",
                        "stderr": "",
                        "old_file":old_file,
                        "new_file":new_file}            
        json.dump(process_output,open(PROCESS_JSON_PATH,'w'),indent=4, sort_keys=True)
        actors_added = self.add_actors_if_exist()               
        StatusBar(self, f"Fertig ! / {process_output['stderr']} / Es sind {actors_added} Darsteller in die DB hinzugefügt worden","#f3f0ff")        
        directory=self.lbl_Ordner.text()

        directory_filename = Path(directory, new_file) 
        err = self.file_rename(directory, old_file, new_file) 
        if Path(directory_filename).exists and not err:                           
            date=self.check_date(self.lnEdit_ProJahr.text())
            actors=self.format_actors(ampers_and=";", comma=";")                                         
            metadata = {
                'Quicktime:CreateDate': self.lnEdit_ErstellDatum.text(),
                'ContentCreateDate#': date,
                'Microsoft:Director': self.lnEdit_Regie.text(),
                'Microsoft:PromotionURL': self.lnEdit_IAFDURL.text(),
                'Microsoft:AuthorURL': self.lnEdit_URL.text(),
                'Microsoft:Writer': self.lnEdit_ProDate.text(),
                'Microsoft:Publisher': self.lnEdit_Studio.text(),
                'Microsoft:Producer': self.lnEdit_NebenSide.text(),
                'Microsoft:EncodedBy': self.lnEdit_ThePornDBURL.text(),
                'Microsoft:Category': self.txtBrw_Tags.toPlainText().strip(),
                'Microsoft:InitialKey': self.lnEdit_SceneCode.text(),
                'ItemList:Artist': actors,
                'ItemList:Title': self.lnEdit_Titel.text(),
                'ItemList:Comment': self.txtBrw_Beschreibung.toPlainText().strip(),
                'ItemList:Genre': self.txtBrw_Movies.toPlainText().strip()  }  
            self.Transfer = uic.loadUi(TRANSFER_UI) 
            self.Transfer.btn_OK_exif.setEnabled(True)
            self.Transfer.btn_OK_exif.raise_()
            self.movie = QMovie(":/labels/_dialog_label/exiftool_processing.gif") 
            self.Transfer.lbl_Dest_Folder.setText("")
            self.Transfer.setWindowTitle("Speichern von MetaTags mit Hilfe von ExifTool !")
            self.Transfer.label_gif_transfer.setMovie(self.movie)
            self.movie.start()        
            self.Transfer.lbl_move_file.setText(new_file)                             
            self.Transfer.lbl_Source_Folder.setText(directory)             
            self.Transfer.prgBar_Transfer.setValue(0)
            self.Transfer.show()
            command = self.create_exiftool_command(directory_filename, metadata)     
            self.startExifSave(directory_filename, command)             
        else:
            StatusBar(self, f"Fehler ! / Datei ist nicht vorhanden !","#F78181")
            MsgBox(self, "Datei ist nicht vorhanden !","w")

    def create_exiftool_command(self, file: str, metadata: dict) -> list:
        command = [EXIFTOOLPFAD, '-m', '-overwrite_original'] 
        for key, value in metadata.items():
            command.append(f'-{key}={value}')  
        command.append(str(file))      
        return command
    
    def add_actors_if_exist(self)-> bool:
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
            name_data["Ordner"]=name
            name_data["Geschlecht"]=1                                               
            errview, artist_neu, sex_neu, link_neu, new_artist_id=database_darsteller.addDarsteller_in_db(name_data, self.lnEdit_Studio.text())
            isda+=artist_neu                 
        for item in range(self.lstWdg_Darsteller.count()):
            name=self.lstWdg_Darsteller.item(item).text() 
            name_data["Name"]=name
            name_data["Ordner"]=name
            name_data["Geschlecht"]=2                        
            errview, artist_neu, sex_neu, link_neu, new_artist_id=database_darsteller.addDarsteller_in_db(name_data, self.lnEdit_Studio.text())
            isda+=artist_neu
        return isda

    def single_DBupdate(self):
        link_items: list = []
        infos_webside = DatenbankSceneMaske(MainWindow=self)

        for index in range(self.model_database_weblinks.rowCount()):
            item = self.model_database_weblinks.data(self.model_database_weblinks.index(index, 0))
            link_items.append(item) 
        WebSideLink="\n".join(link_items)

        if self.tabs.currentIndex() == 2:        
            studio=self.Btn_logo_am_db_tab.toolTip()
        else:
            studio=self.Btn_logo_am_infos_tab.toolTip()                       
        infos_webside.update_db_and_ui(studio, WebSideLink) 
    
    def show_database_for_performers(self):
        self.clear_mask()
        self.Btn_DBArtist_Update.setEnabled(False)             
        performer_infos_maske = PerformerInfosMaske(MainWindow=self)
        performer_infos_maske.artist_infos_in_maske()

    def show_database_for_movies(self): 
        self.clear_mask("movie")
        self.datenbank_save("delete")
        self.model_database_weblinks.clear()        
        self.tblWdg_DB_performers.setRowCount(0)                       
        self.lnEdit_DBTitel.setText(self.tblWdg_daten.selectedItems()[1].text())
        self.tabs.setCurrentIndex(2)  # Tab für Datenbank aktiv
        infos_webside = DatenbankSceneMaske(MainWindow=self)
        infos_webside.set_datas_in_database()
        ClearingWidget(self).enabled_db_buttons(True)

    def clear_mask(self, type: str=None) -> None:
        clearing = ClearingWidget(self)         
        elements_to_reset = ["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Movies", "Synopsis", "Tags"]            
        for widgets in elements_to_reset:
            clearing.tooltip_claering(widgets)
        if type=='movie':
            for widget_name in ["DBData18Link", "DBIAFDLink"]:
                clearing.clear_line_edit_and_tooltip(widget_name)    

    def addLink(self):        
        link = self.lnEdit_addLink.text()
        zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
        if link.startswith("https://"):            
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
                self.lbl_db_status.setText(f"{zeit}: »{selected_text}« wurde gelöscht !")
            else:
                self.lbl_db_status.setText(f"{zeit}: Ungültige Auswahl.")
        else:
            self.lbl_db_status.setText(f"{zeit}: Kein Element ausgewählt.")


    def add_performers(self,name: str="",alias: str="",action: str="") -> None:
        self.tblWdg_DB_performers.setRowCount(self.tblWdg_DB_performers.rowCount()+1) 
        self.tblWdg_DB_performers.setItem(self.tblWdg_DB_performers.rowCount()-1,0,QTableWidgetItem(name))
        self.tblWdg_DB_performers.setItem(self.tblWdg_DB_performers.rowCount()-1,1,QTableWidgetItem(alias))       
        self.tblWdg_DB_performers.setItem(self.tblWdg_DB_performers.rowCount()-1,2,QTableWidgetItem(action))
        self.tblWdg_DB_performers.setCurrentCell(self.tblWdg_DB_performers.rowCount()-1, 0)
    
    def del_performers(self):
        row_index = self.tblWdg_DB_performers.currentRow()
        if row_index >= 0:
            self.tblWdg_DB_performers.removeRow(row_index)

    def add_db_in_datei(self):        
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

        actors: list=[]
        for zeile in range(self.tblWdg_DB_performers.rowCount()):
            actors.append(self.tblWdg_DB_performers.item(zeile, 0).text()) 
        self.add_actors_in_ui(actors)

        self.lnEdit_Titel.setText(self.lnEdit_DBTitel.text())
        self.lnEdit_URL.setText(self.lstView_database_weblinks.model().data(self.lstView_database_weblinks.model().index(0, 0)))
        self.lnEdit_ErstellDatum.setText(self.lnEdit_DBRelease.text())
        self.lnEdit_ThePornDBURL.setText(self.lnEdit_DBThePornDBLink.text())        
        self.lnEdit_IAFDURL.setText(self.lnEdit_DBIAFDLink.text())
        self.lnEdit_ProJahr.setText(self.lnEdit_DBProDate.text()[-4:] if self.lnEdit_DBProDate.text() else self.lnEdit_DBRelease.text()[:4])
        self.lnEdit_ProDate.setText(self.lnEdit_DBProDate.text())
        self.lnEdit_NebenSide.setText(self.lnEdit_DBSerie.text().replace(" ",""))        
        self.lnEdit_Regie.setText(self.lnEdit_DBRegie.text()) 
        self.txtBrw_Movies.setText(self.txtEdit_DBMovies.toPlainText())       
        self.lnEdit_SceneCode.setText(self.lnEdit_DBSceneCode.text())                
        self.txtBrw_Beschreibung.setText(self.txtEdit_DBSynopsis.toPlainText())      
        self.txtBrw_Tags.setText(self.txtEdit_DBTags.toPlainText()) 
        gesuchter_text = self.lbl_Dateiname.text()[:-4]
        self.activate_item(gesuchter_text)  

    def add_all_pornbox_links(self):
        self.lstView_database_weblinks.model().removeRows(0, self.lstView_database_weblinks.model().rowCount())
        letter = self.lnEdit_DBTitel.text()[-6:]
        data18_link = self.lnEdit_DBData18Link.text()
        tpdb_link = self.lnEdit_DBThePornDBLink.text()
        iafd_link = self.lnEdit_DBIAFDLink.text().lower()
        movie = self.txtEdit_DBMovies.toPlainText()
        PornBoxLinks(self).hole_links_von_PornWorld(letter, data18_link, tpdb_link, iafd_link,  movie) 
        studio = self.Btn_logo_am_db_tab.toolTip() 
        self.get_video_data_from_database(studio, self.lnEdit_DBTitel.text())
        self.show_database_for_movies()  

    def startExifSave(self, source_path: str, command: str) -> None:
        self.Transfer.btn_OK_exif.setEnabled(False)        
        self.ExifSaveThread = ExifSaveThread(source_path, command)
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
        self.Transfer.label_gif_transfer.setPixmap(QPixmap(":/labels/_dialog_label/Info.jpg")) 
        minutes_start, seconds_start = divmod(start_time, 60)        
        self.Transfer.lbl_speed.setText(f"{speed:.2f} MB/s - nach Ende: {minutes_start:02d}:{seconds_start:02d}s > FERTIG ! {process_output['stdout']}")
        self.Transfer.btn_OK_exif.clicked.connect(lambda: self.ordner_transfer_zurueck(True))
         
        
    def check_date(self,datum : str) -> str:
        if datum:
            datum=str(self.lnEdit_ErstellDatum.text())[:4]       
        return ("20"+datum)[-4:] 
    
    def file_rename_from_infos(self):
        self.file_rename(self.lbl_Ordner.text(),self.lbl_Dateiname.text(),"")

    ### -------------------- datei umbenennen --------------------- ###
    def file_rename(self, directory: str, old_file: str, new_file: str = "") -> str: 
        if old_file == new_file:
            return None
        
        if not new_file:
            new_file = self.file_format(new_file)                
            process_output = json.loads(PROCESS_JSON_PATH.read_bytes())
            process_output["new_file"] = new_file
            json.dump(process_output, open(PROCESS_JSON_PATH, 'w'), indent=4, sort_keys=True)

        try:
            Path(directory, old_file).rename(Path(directory, new_file))
        except OSError as os_err:
            if os_err.errno == errno.EACCES:
                os_err = "Die Datei ist noch geöffnet, bitte schließen!"
            MsgBox(self, f"Fehler !<br>{os_err}</br>", "w")
            return str(os_err)
        else:
            self.lbl_Dateiname.setText(new_file)
            self.refresh_table(new_file[:-4])            
        return None
    
    ### ------- file_format, nach bekannten Muster vorbereiten ---------- #
    def check_studio(self, studio_name: str, titel: str) -> Tuple[str, str]:
        if studio_name in ["GirlCum", "NubilesPorn"] and "Orgasms" in titel:
            titel = titel.replace(" - ", "[") + "]"
        if studio_name:
            studio_name=f"{studio_name} - "
        return studio_name, titel
    
    def file_format(self, new_file) -> str:
        studio_name: str  = self.lnEdit_Studio.text()
        titel: str = self.lnEdit_Titel.text()
        neben_side = f"[{self.lnEdit_NebenSide.text().replace(' ', '')}]" if self.lnEdit_NebenSide.text() else ""
        studio_name, titel = self.check_studio(studio_name, titel) 
               
        actors = self.windows_file_filter(self.format_actors(" & ", ", ").replace("(m)", "").replace("-", ""))        
        return f"{studio_name}{actors}-{titel}{neben_side}.mp4" 
    ### ------------------------------------------------------------------ #       

    def Infos_ExifToolHolen(self) -> None:        
        ClearingWidget(self).tabs_clearing(False, False) 
        filename=self.lbl_Dateiname.text()
        self.lbl_datei_info_fuer.setText(filename)       
        directory_filename = Path(self.lbl_Ordner.text(), filename)        
        error = self.load_exiftool_json(directory_filename)

        if not error and MEDIA_JSON_PATH.exists():
            self.metatags_in_ui_laden()
            db_webside_settings = Webside_Settings(MainWindow=self)
            errorview, studio, logo = db_webside_settings.get_buttonlogo_from_studio(self.lnEdit_Studio.text())
            if not studio:
                logo="background-image: url(':/Buttons/_buttons/no-logo_90x40.jpg')"
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
        self.split_actors_and_put_ui(file_media_info.get("Artist")) 

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
                    "EncodedBy":self.lnEdit_ThePornDBURL,      }
        for atom,item in atom_dict.items(): 
            if file_media_info.get(atom):                                                                
                inhalt=file_media_info.get(atom)                    
                item.setText(str(inhalt))

    def split_actors_and_put_ui(self, actor_string: str) -> None:
        if actor_string is not None:       
            actors = [actor.replace("(m)","").strip() for actor in re.split('[;/]', actor_string) if actor.strip()]                                   
            self.add_actors_in_ui(actors)
        
    def set_analyse_daten(self):
        clearing = ClearingWidget(self)
        clearing.buttons_enabled(False, ["logo_am_analyse_tab", "name_suche", "titel_suche"])

        filename: str=self.lbl_Dateiname.text()

        self.lbl_analyse_fuer.setText(filename)        
        studio_name, titel, artist = self.filename_analyse(filename)
        self.grpBox_analyse_name.setTitle(f"Darstellername:       Anzahl: {len(artist)}")

        db_webside_settings = Webside_Settings(MainWindow=self)               
        errorview, studio, logo = db_webside_settings.get_buttonlogo_from_studio(studio_name)
        
        if artist:
            clearing.buttons_enabled(True, ["logo_am_analyse_tab", "name_suche"])
            self.cBox_performers.clear()
            for item in artist:
                self.cBox_performers.addItem(item)                                           
            
            self.is_studio_in_database(studio)

        if studio:                    
            self.Btn_logo_am_analyse_tab.setEnabled(True)
            self.lbl_SuchStudio.setText(studio)                   
            self.Btn_logo_am_analyse_tab.setStyleSheet(logo)
            self.Btn_logo_am_analyse_tab.setToolTip(studio)
            clearing.buttons_enabled(True, ["logo_am_analyse_tab", "name_suche", "titel_suche"])

            if titel:
                self.lnEdit_analyse_titel.setText(titel)
                self.Btn_titel_suche.setEnabled(True) 
        else:
            logo="background-image: url(':/Buttons/_buttons/no-logo_90x40.jpg')"
            studio="kein Studio ausgewählt !"
            self.lnEdit_analyse_titel.setText(studio)

    def is_studio_in_database(self, studio: str) -> bool:
        studio_isin: bool = False

        scraping_data = ScrapingData(MainWindow=self)
        studio_isin = scraping_data.is_studio_in_db(studio)

        clearing=ClearingWidget(self)
        if studio_isin:
            clearing.buttons_enabled(True,["VideoDatenHolen"])
            
            if studio in ["BangBros"]:
                clearing.special_infos_visible(True)
            else:
                clearing.special_infos_visible(False)
        else:
            clearing.buttons_enabled(False,["VideoDatenHolen"])

        return studio_isin
    
    def add_actors_in_ui(self, actors: list) -> None:
        if self.tabs.currentWidget() == self.tab_info:
            widget_variable_w = self.lstWdg_Darstellerin
            widget_variable_m = self.lstWdg_Darsteller
            widget_variable_w.clear()
            widget_variable_m.clear()            
            custom_widget = QWidget()            
            custom_widget.setAutoFillBackground(True)
            database_darsteller = DB_Darsteller(MainWindow=self)
            for performer in actors:
                item = QListWidgetItem(performer)                
                is_vorhanden, geschlecht = database_darsteller.isdaDarsteller(performer)                
                if is_vorhanden:
                    item.setBackground(QBrush(QColor("#e9ff1d")))
                    if geschlecht > 1:                        
                        widget_variable_m.addItem(item)
                    else:
                        widget_variable_w.addItem(item)
                else:
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
                websides = DatenbankSceneMaske(MainWindow=self)
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