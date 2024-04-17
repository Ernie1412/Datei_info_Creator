from PyQt6.QtGui import QPixmap, QMovie, QColor
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QTableWidgetItem


import requests
from lxml import html, etree
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError
import time

import re
import ast
from pathlib import Path
from utils.database_settings.database_for_settings import Webside_Settings
from utils.web_scapings.datenbank_performer_maske import DatenbankPerformerMaske
from gui.helpers.message_show import StatusBar

from config import HEADERS, PROJECT_PATH


class LoadPerformerImages():

    def __init__(self, ordner, MainWindow):
        super().__init__() 
        self.Main = MainWindow                        
        self.ordner = ordner

    def open_url(self, url, studio, java, image_url_xpath):
        content=None
        if java:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()                 
                try:
                    page.goto(url, timeout=10000) 
                    page.wait_for_selector(image_url_xpath) 
                except TimeoutError as e:
                    StatusBar(self.Main,f"Fehler beim laden vom Image-Daten(Java). Fehler: {e} bei Studio: {studio}","#FF0000")                    
                else: 
                    content = html.fromstring(page.content())
                    # with open(str(PROJECT_PATH / 'index.html'), 'w') as f:
                    #     f.write(page.content())
                finally:
                    browser.close()
                    return content
        else:
            try:
                with requests.Session() as session:
                    response = session.get(url, headers=HEADERS, timeout=10)                                                 
            except (requests.exceptions.Timeout, requests.exceptions.RequestException, Exception) as e:
                StatusBar(self.Main,f"Fehler beim laden vom Image-Daten(no Java). Fehler: {e} bei Studio: {studio}","#FF0000")                 
            else:
                content = html.fromstring(response.content)
                # with open(str(PROJECT_PATH / 'index.html'), 'wb') as f:
                #     f.write(response.content)                 
            finally:            
                return content  

    def get_table_data(self, row, column):
        index = self.Main.tblWdg_performer_links.model().index(row, column) 
        return self.Main.tblWdg_performer_links.model().data(index)  

    def load_website_image_in_label(self): 
        image_url: str=""
        current_row = self.Main.tblWdg_performer_links.currentRow()
        url = self.get_table_data(current_row, 1) 
        base_url = self.get_base_url(url)
        webside_settings = Webside_Settings(MainWindow=self.Main)
        name_element_xpath, name_element_attri, name_element_title, image_url_xpath, image_url_attri, studio, java = webside_settings.hole_artist_image(base_url)
        
        content = self.open_url(url, studio, java, image_url_xpath)
        if content is None:            
            return 
        name_element_xpath = name_element_xpath.split("\n")
        try: 
            name_element = content.xpath(name_element_xpath[0])
            if len(name_element) == 0:
                if len(name_element_xpath)== 2 and len(content.xpath(name_element_xpath[1]))== 1:
                    raise ValueError("Link ist nicht mehr vorhanden ! (Error 404)")
                raise ValueError("Kein WebElement gefunden")
        except (etree.XPathEvalError, TypeError, ValueError) as e:
            StatusBar(self.Main,f"Fehler beim laden vom Image-Name. Fehler: {e} bei Studio: {studio}","#FF0000")
            self.Main.tblWdg_performer_links.setItem(current_row,2,QTableWidgetItem(""))
            DatenbankPerformerMaske(self.Main).setColortoRow(self.Main.tblWdg_performer_links,current_row, '#FFFD00') 
            return
        try:
            image_element = content.xpath(image_url_xpath)
            if len(image_element) == 0:
                raise ValueError("Kein WebElement gefunden")
        except (etree.XPathEvalError, TypeError, ValueError) as e:
            StatusBar(self.Main,f"Fehler beim laden vom Image. Fehler: {e} bei Studio: {studio}","#FF0000")
            return                
        alias = self.get_alias(name_element[0], name_element_attri, name_element_title)
        
        label_height = 280
        label_width = 0
        pixmap = QPixmap()
        image_pfad = ""
        if image_element:
            image_url = self.get_image_url(image_url_attri, url, base_url, image_element[0]) 
            try: 
                if not image_url:
                    raise ValueError
                response = requests.get(image_url, headers=HEADERS)
            except requests.exceptions.MissingSchema:
                StatusBar(self.Main,f"Es ist kein Bild auf der Webside des Studios '{studio}' zu sehen (Dummy)","#FF0000")
                self.image_label_set_kein_bild()
                return
            except ValueError:
                StatusBar(self.Main,f"Es ist kein Bild auf der Webside des Studios '{studio}' vorhanden !","#FF0000")
                self.image_label_set_kein_bild()
                return    
            else:                
                pixmap.loadFromData(response.content)   
                id=self.get_id(url)
                image_pfad=f"__artists_Images/{self.ordner}/[{studio}]-{id}.jpg"                
                try:
                    label_width = int(label_height * pixmap.width() / pixmap.height())
                except ZeroDivisionError as e:
                    self.Main.lbl_db_status.setText(f"load_website_image_in_label: {self.Main.lnEdit_performer_info.text()} --> Fehler: {e}")
                    self.image_label_set_kein_bild()
                    return                                 
                self.check_folder(image_pfad)
                pixmap.save(str(PROJECT_PATH / image_pfad), "JPEG") 
        # finally: Ausgabe in die Tabelle 
        self.set_image_result_in_ui(alias, current_row, label_width, label_height, image_pfad, pixmap)        
    
    def set_image_result_in_ui(self, alias: str, current_row: int, label_width: int, label_height: int, image_pfad: str, pixmap: QPixmap) -> None:
        self.Main.tblWdg_performer_links.setItem(current_row,3,QTableWidgetItem(alias))        
        self.Main.tblWdg_performer_links.setItem(current_row,2,QTableWidgetItem(image_pfad))
        if (alias or image_pfad):
            DatenbankPerformerMaske(self.Main).setColortoRow(self.Main.tblWdg_performer_links,current_row, '#FFFD00')
        if image_pfad:
            self.Main.Btn_performer_next.setGeometry(label_width+20,140,20,50)                                                
            self.Main.lbl_link_image_from_db.setGeometry(20, 20, label_width, label_height)         
            self.Main.lbl_link_image_from_db.setPixmap(pixmap)
        else: 
            self.image_label_set_kein_bild()

    def image_label_set_kein_bild(self):
        pixmap = QPixmap(":/labels/_labels/kein-bild.jpg") #560x660                   
        self.Main.lbl_link_image_from_db.setPixmap(pixmap.scaled(240, 280, Qt.AspectRatioMode.KeepAspectRatio))        

    def check_folder(self, image_pfad):
        ordner=Path(PROJECT_PATH / image_pfad).parent
        if not Path(ordner).exists():
            Path(ordner).mkdir()

    def get_id(self, u):
        filter_terms=["/star/", "/model/", "/pornstar/", "/models/","/girls/", "/girl/", "/perfid="] 
        replace_rules = [("/", "_"), ("gender=", ""), (".htm", ""), ("ame014/1/","")]
        u = urlparse(u.replace("/en/", "/")).path.lower()
        for term in filter_terms:
            if term in u:
                id_value = u.split(term)[-1]
                for old, new in replace_rules:
                    id_value = id_value.replace(old, new)
                return id_value
        return ""
    
    def get_alias(self, name_element, name_element_attri: str, name_element_title: str) -> str:
        alias = ""
        if name_element is not None: 
            regex = ast.literal_eval(name_element_attri)           
            alias = re.sub(regex, "", name_element.text_content()) 
            alias = alias.title() if name_element_title else alias
        return alias

    def get_image_url(self, image_url_attri: str, url: str, base_url: str, image_element) -> str:
        if not image_url_attri:
            return ""
        else:
            baseurl: str=""
            if image_url_attri.startswith("/"):
                image_url_attri = image_url_attri.replace("/","")
                baseurl = base_url
            image_url = f"{baseurl}{image_element.get(image_url_attri)}"
            image_url = f"https:{image_url}" if image_url.startswith("//") else image_url
        return image_url            

    def get_base_url(self, url):
        return urlparse(url).scheme +"://"+urlparse(url).netloc+"/"
    

if __name__ == '__main__':
    LoadPerformerImages()


