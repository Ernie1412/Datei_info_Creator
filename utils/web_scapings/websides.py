### Grafik Oberfläche ###
from PyQt6.QtCore import QTimer, QCoreApplication
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QTableWidgetItem, QApplication, QTableWidgetSelectionRange, QMessageBox
### internet Kram ###
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException,TimeoutException,InvalidSelectorException,SessionNotCreatedException, WebDriverException

from playwright.sync_api import sync_playwright, TimeoutError

import requests
from lxml import html
### ---------------- ###
import pyperclip
import re
import copy
import pandas as pd
from datetime import datetime
from typing import Union, Optional, List, Tuple

# import eigene Moduls
from utils.database_settings import Webside_Settings, DB_WebSide
from utils.web_scapings.scrap_with_requests import VideoUpdater
from utils.umwandeln import time_format_00_00_00, datum_umwandeln, from_classname_to_import
from gui.dialoge_ui import StatusBar, MsgBox


from config import HEADERS, selenium_browser_check

class Infos_WebSides():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow   

    #### ------------ Anzeige ob IAFD, DATA Check negativ,checking, Loading,  OK und error ist ! --------- ####
    #### --------------------------------------------------------------------------------------- ####
    def check_negativ_labelshow(self,widget: str) -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setText("check negativ !")
        getattr(self.Main, f"Btn_Linksuche_in_{widget}").setEnabled(False)
        QTimer.singleShot(500, lambda :getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #FF0000'))
        QTimer.singleShot(3000, lambda :getattr(self.Main, f"lnEdit_DB{widget}Link").setText(""))
        QTimer.singleShot(3500, lambda :getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #FFFDD5'))        
        QTimer.singleShot(3500, lambda :getattr(self.Main, f"lbl_checkWeb_{widget}URL").setVisible(False))
    
    def just_checking_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #AAFFFF')        
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setVisible(True)
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setText(f"Check {widget} !")
        QApplication.processEvents()
    
    def check_OK_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"Btn_Linksuche_in_{widget}").setEnabled(True)
        getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #74DF00')
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setText("Check OK !")

    def check_error_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setText("Check-Fehler !")
        QTimer.singleShot(2000, lambda :getattr(self.Main, f"lbl_checkWeb_{widget}URL").setText(""))
        getattr(self.Main, f"Btn_Linksuche_in_{widget}").setEnabled(False)            
        getattr(self.Main, f"lnEdit_DB{widget}Link").setText("")
        getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #FFFDD5')

    def check_loading_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setText("Seite wird geladen !") 
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setToolTip("") 
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").repaint()

    def check_loaded_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setText("OK, Seite geladen !") 

    def fehler_ausgabe_checkweb(self, error, widget: str) -> None:
        MsgBox(self.Main, error,"w")        
        code = error.code if hasattr(error, 'code') else "N/A"            
        getattr(self.Main, f"lbl_checkWeb_{widget}").setText(f"Error: {code}")            
        getattr(self.Main, f"lbl_checkWeb_{widget}").setToolTip(str(error))       
    #### --------------------------------------------------------------------------------------- ####

    def Web_Data18_change(self):
        webdatabase: str="Data18"
        self.just_checking_labelshow(webdatabase)                      
        if self.Main.lnEdit_DBData18Link.text().startswith("https://www.data18.com/"):                         
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                url = self.Main.lnEdit_DBData18Link.text() 
                try:
                    page.goto(url, timeout=5000)
                except TimeoutError as e:
                    self.fehler_ausgabe_checkweb(e,"Data18URL") 
                    self.check_negativ_labelshow(webdatabase)                     
                else:
                    self.check_OK_labelshow(webdatabase)                
                finally:
                    browser.close()
        else:
            self.check_error_labelshow(webdatabase)      


    def webscrap_data18(self):
        self.check_loading_labelshow("Data18")              
        url = self.Main.lnEdit_DBData18Link.text() 

        felder = ["Release", "Dauer", "Serie", "Synopsis", "Movies", "QuellSide"]
        self.abfragen_data18(url, felder)

        self.check_loaded_labelshow("Data18") 
              

    def abfragen_data18(self, url: str, felder: list) -> None:
        self.Main.txtEdit_Clipboard.setPlainText("Scraping Data18 Element:")         
        status: str="Error"
        orginal_page: str=None 
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()            
            time_out = 2000                            
            try:
                page.goto(url, timeout=5000)
                page.locator("//button[contains(string(),'ENTER - data18.com')]").click()                              
            except TimeoutError as e:
                self.fehler_ausgabe_checkweb(e,"Data18URL")
                self.scrap_status("URL Loading...", "Timeout Error: 5000ms")  
            else:
                self.scrap_status("URL Loading...", "OK") 
                page.set_default_timeout(time_out)               
                for feld in felder:
                    if feld == "Release":
                        try:
                            release_ele = page.locator('//span[@class="gen12"]/b/following::a[1]/b')
                            release_text = release_ele.inner_text()
                        except (TimeoutError, AttributeError):
                              release_text = None 
                              status=f"Kein Release Datum gefunden - Timeout: {time_out}ms"
                        else: 
                            status = "OK"                            
                            self.release_abfrage_data18(release_text, url)  
                        self.scrap_status(feld, status)
                    elif feld == "Dauer":
                        try:
                            dauer_ele = page.locator( "//div[@class='gen12']/p | //div[@class='gen12']/b")
                            dauer_text = dauer_ele.nth(0).inner_text()  
                        except (TimeoutError, AttributeError):
                              dauer_text = None 
                              status=f"Keine Runtime gefunden - Timeout: {time_out}ms"
                        else:
                            status = "OK"                            
                            self.dauer_abfrage_data18(dauer_text, url)
                        self.scrap_status(feld, status)
                    elif feld == "Serie": 
                        try:
                            serie_ele = page.locator("//p[contains(., 'Network')]/a[@class='bold']")
                            serie_text = serie_ele.nth(0).inner_text() 
                        except (TimeoutError, AttributeError):
                            status = f"Keine Serie/Sub-Side gefunden - Timeout: {time_out}ms"                       
                        else:
                            status = "OK" 
                            self.serie_abfrage_data18(serie_text, url) 
                        self.scrap_status(feld, status)                            
                    elif feld == "Synopsis":
                        try:
                            synopsis_text = page.locator("//div[@class='gen12']/div[starts-with(string(),'Story')]").inner_text()                             
                        except (TimeoutError, AttributeError):
                            status = f"Keine Synopsis gefunden - Timeout: {time_out}ms" 
                        else:
                            status = "OK"                                                         
                            self.synopsis_abfrage_data18(synopsis_text, url)
                        self.scrap_status(feld, status) 
                    elif feld == "Movies":                        
                        try:
                            movie_element = page.locator("//p/b[contains(.,'Movie')]/following::a[1]")                           
                            movie_text = movie_element.inner_text()
                        except (TimeoutError, AttributeError):
                              movie_text, scene_text, studio_texts = None, None, None 
                              status = f"Kein Movie gefunden - Timeout: {time_out}ms"
                        else: 
                            status = "OK"
                            movie_url = movie_element.get_attribute('href')                                                      
                            scene_text = page.locator("//div[contains(@class, 'relatedmovie_zone')]/div[contains(i, 'Current scene')]").inner_text()        
                            studio_texts = page.locator("//a[contains(@href,'https://www.data18.com/studios/')]").all_text_contents()                            
                            page.goto(movie_url, timeout=5000)                                                        
                            jahr: int=0
                            try:
                                jahr = int(page.locator("//p[contains(string(),'Prod. Year:')]/b").inner_text())
                            except (TimeoutError, AttributeError):
                                pass
                            else:
                                links = self.Main.lstView_database_weblinks.model().data(self.Main.lstView_database_weblinks.model().index(0, 0))                                 
                                studio_texts = self.pipeline_movie_distr(links, jahr)
                                self.movies_abfrage_data18(movie_text, scene_text, studio_texts, jahr, url) 
                        self.scrap_status(feld, status)
                    elif feld == "QuellSide":
                        try:
                            page.go_back()
                            quell_side_element = page.locator('//a[@class="ext"]').nth(0)                             
                        except (TimeoutError, AttributeError): 
                            status = f"Kein Quell Side gefunden - Timeout: {time_out}ms"                                       
                        else:
                            status = "OK"
                            quell_side_url = quell_side_element.get_attribute('href') 
                            try:                           
                                page.goto(quell_side_url, timeout=5000)
                            except (TimeoutError, AttributeError) as e:
                                status = f"Fehler: {e} - {quell_side_url}"                               
                            else:
                                current_url = page.url                           
                                next_url = re.search(r'^(.*?)\?([^\?&]{1,10})=', current_url).group(1) if re.search(r'^(.*?)\?([^\?&]{1,10})=', current_url) else next_url
                                urls=self.pipeline_add_link(next_url)                                
                                for url in urls.split("\n"):
                                    if not self.is_url_in_model(url):
                                        self.Main.model_database_weblinks.appendRow(QStandardItem(url))
                        self.scrap_status(feld, status)
            finally:
                browser.close()  

    def pipeline_add_link(self, url):
        links = url
        baselink = "/".join(url.split("/")[:3])+"/"

        db_webside_settings = Webside_Settings(self)      
        errorview, spider_class_name = db_webside_settings.from_link_to_spider(baselink)        
        if not errorview:
            spider_class_pipeline = from_classname_to_import(spider_class_name, pipeline="Pipeline") ## import der Klasse "Pipeline"
            if spider_class_pipeline: 
                # Rufe die Funktion auf
                instance = spider_class_pipeline()
                links = instance.add_link(url)
        return links

    def pipeline_movie_distr(self, url, jahr):        
        baselink = "/".join(url.split("/")[:3])+"/"        
        db_webside_settings = Webside_Settings(self)      
        errorview, spider_class_name = db_webside_settings.from_link_to_spider(baselink) 
        errorview, distr = db_webside_settings.from_link_to_studio(baselink)            
        if not errorview:            
            spider_class_pipeline = from_classname_to_import(spider_class_name, pipeline="Pipeline") ## import der Klasse "Pipeline"
            if spider_class_pipeline: 
                # Rufe die Funktion auf
                instance = spider_class_pipeline()
                distr = instance.movie_distr(spider_class_name, jahr)
        else:
            distr = url
        return distr.split("\n")      
    
    def is_url_in_model(self, url):
        for row in range(self.Main.model_database_weblinks.rowCount()):
            item = self.Main.model_database_weblinks.item(row)
            if item is not None and item.text() == url:
                return True
        return False

    def release_abfrage_data18(self, release_text, url):
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Release","Data18")  
        
        status = "OK"                    
        tooltip_text = f"{quelle}: ({len(release_text)}) -> {release_text}" 
        release_date = datum_umwandeln(release_text, "%B %d, %Y")             
        self.set_daten_in_maske(maske_typ, feld, url, release_date)
        
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        

    def dauer_abfrage_data18(self, dauer_text: str, url: str) -> None:
        ### die Runtime Abfrage ###
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Dauer","Data18")        
                    
        if "Membership Site: " in dauer_text:
            membership_start = dauer_text.find("Membership Site: ") + 17
            dauer_text = dauer_text[membership_start:]
        dauer_text = time_format_00_00_00(dauer_text)
        tooltip_text = f"{quelle}: -> {dauer_text}"
        self.set_daten_in_maske(maske_typ, feld, url, dauer_text)
        
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)           

    def serie_abfrage_data18(self, serie_text: str, url: str) -> None:
        ### Abfrage nach Nebenside bzw Serie ### 
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Serie","Data18")        
            
        serie_text = serie_text.title() if " " in serie_text else serie_text
        self.set_daten_in_maske(maske_typ, feld, url, serie_text)
        tooltip_text = f"{quelle}: -> {serie_text}"
        
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        

    def movies_abfrage_data18(self, movie_text: str, scene_text: str, studio_texts: list, jahr: int, url: str) -> None:
        ### Abfrage nach möglichen Film-Release ###
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Movies","Data18")         
                    
        scene_text = re.search(r'Scene \d+', scene_text).group() if re.search(r'Scene \d+', scene_text) else "Scene N/A"                     
        studio_text = studio_texts[0].replace(" ","")        

        tooltip_text = f"{quelle}: -> {movie_text}"
        self.set_daten_in_maske(maske_typ, feld, url, f"{scene_text}: {studio_text} - {movie_text}({jahr})FULLHD-ENGLISH") 
        
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        return status

    def synopsis_abfrage_data18(self, synopsis_text: str, url: str) -> None:
        ### Abfrage nach einer Beschreibung ### 
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Synopsis","Data18")        
                   
        tooltip_text = f"{quelle}: ({len(synopsis_text[8:])}) -> {synopsis_text[8:40]}"
        self.set_daten_in_maske(maske_typ, feld, url, synopsis_text[8:].replace("�",'').replace("\xa0", " "))
        
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        return status

    ##### -------------- Alles von IAFD ------------------- ##### 
    ##### ------------------------------------------------- #####
    def Web_IAFD_change(self):
        webdatabase: str="IAFD"

        self.just_checking_labelshow(webdatabase) 
        if self.Main.lnEdit_DBIAFDLink.text().startswith("https://www.iafd.com/title"):                    
            r = requests.get(self.Main.lnEdit_DBIAFDLink.text(), headers=HEADERS)                
            if len(html.fromstring(r.content).xpath('//div[@class="col-sm-12"]/h1/text()'))==1:
                self.check_OK_labelshow(webdatabase)
            else:
                self.check_negativ_labelshow(webdatabase)  
        else:
            self.Main.lnEdit_IAFD_titel.setText(self.Main.lnEdit_DBTitel.text())
            self.Main.lnEdit_db_jahr.setText(self.Main.lnEdit_DBRelease.text()[:4])
            self.Main.stackedWidget.setCurrentIndex(3)
            self.check_error_labelshow(webdatabase)

    def webscrap_iafd(self):
        self.check_loading_labelshow("IAFD")
        url = self.Main.lnEdit_DBIAFDLink.text()        
        content = self.open_url_no_javascript(url)

        self.regie_abfrage_iafd(content, url)
        self.dauer_abfrage_iafd(content, url)
        sub_side = self.serie_abfrage_iafd(content, url)
        self.releasedate_abfrage_iafd(content, url)
        self.titel_abfrage_iafd(content, url)
        self.akas_abfrage_iafd(content, url, sub_side)
        self.synopsis_abfrage_iafd(content, url)
        self.performers_abfrage_iafd(content, url)        

    ### Wenn der Titel da ist und min. 1 Darsteller da ist, Speicher-Button aktiv ###
        if self.Main.lnEdit_DBTitel.text() and self.Main.tblWdg_Files.currentColumn() != -1:
            self.Main.Btn_Speichern.setEnabled(True)        
        self.check_loaded_labelshow("IAFD")

    def open_url_no_javascript(self, url: str) -> html.Element: 
        status: str = "Error"
        response: str = None
        content: str = None                     
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            self.fehler_ausgabe_checkweb(e,"IAFDURL") 
            status = e           
        else:
            status = "OK"
            content = html.fromstring(response.content)
        self.scrap_status(f"{url} wird geöffnet", status)
        return content
    
    def scrap_status(self, feld: str, status: str) -> None:        
        text = self.Main.txtEdit_Clipboard.toPlainText()
        umbruch = "\n" if text !="" else ""            
        self.Main.txtEdit_Clipboard.setPlainText(f"{text}{umbruch}Scrape: {feld} <-- {status}")
        QCoreApplication.instance().processEvents()
    
    def initialisize_abfrage(self, feld: str, quelle: str) -> Tuple[str, str, str, str, str]:
        status: str = "Error"
        if feld in ["Movies", "Tags", "Synopsis"]:
            maske_typ: str = "txtEdit_DB"
        else:
            maske_typ: str = "lnEdit_DB"               
        tooltip_text: str = f"{quelle}: kein Eintrag gefunden"
        return status, maske_typ, feld, quelle, tooltip_text
    

    def regie_abfrage_iafd(self, content: html.Element, url):        
        ### Regie Abfrage ###  
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Regie","IAFD")        

        regie_element = content.xpath("//p[contains(string(),'Director')]/following::p[1]/text() | //p[contains(string(),'Director')]/following::p[1]/a/text()")
        if regie_element:
            tooltip_text = f"{quelle}: {regie_element[0]}"
            status = "OK"
            if regie_element[0] != "No Director Credited" and regie_element[0] != "No Data": 
                self.set_daten_in_maske(maske_typ, feld, url, regie_element[0])

        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        self.scrap_status(feld, status)

    def dauer_abfrage_iafd(self, content: html.Element, url):
        ### die Runtime Abfrage, Sekunden mit :00 auffüllen ###
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Dauer","IAFD")        

        dauer = content.xpath("//p[contains(.,'Minutes')]/following::p[1]/text()")        
        if dauer: 
            status ="OK"
            tooltip_text = f"{quelle}: {dauer[0]}"
            if dauer[0] != "No Data":
                dauer=self.minutes_to_hhmmss(int(dauer[0]))
                self.set_daten_in_maske(maske_typ, feld, url, dauer)

        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        self.scrap_status(feld, status)

    def serie_abfrage_iafd(self, content: html.Element, url: str) -> str:
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Serie","IAFD")                

        ### Studio und Serie, falls vorhanden Abfrage ###
        studio_element = content.xpath("//p[contains(.,'Studio')]/following::p[1]/a")
        if studio_element:
            status = "OK"            
            tooltip_text = f"{quelle}: {studio_element[0].text}"
            db_webside_settings = Webside_Settings(self.Main)
            studio, serie = db_webside_settings.from_studio_to_subside_for_iafd(studio_element[0].text)            
            self.set_daten_in_maske(maske_typ, feld, url, serie)            

        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        self.scrap_status(feld, status)
        return studio
    

    def releasedate_abfrage_iafd(self, content: html.Element, url: str) -> None:
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Release","IAFD")         

        ### Release-Date Abfrage, Windows-Konform umwandeln ###
        release_date_elements = content.xpath("//p[contains(.,'Release Date')]/following::p[1]")

        if release_date_elements:
            status = "OK" 
            release_text = release_date_elements[0].text.strip()
            tooltip_text = f"{quelle}: {release_text}"
            if "no data" not in release_text.lower():
                release_date = datetime.strptime(release_text, "%b %d, %Y").strftime("%Y:%m:%d")+ " 00:00:00"
                self.set_daten_in_maske(maske_typ, feld, url, release_date)                
            
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        self.scrap_status(feld, status)

    def titel_abfrage_iafd(self, content: html.Element, url: str) -> None:
        ### Titel Abfrage, das Jahr "(2023)" cutten ###
        if self.Main.lnEdit_DBTitel.text() == "": ## wenn kein Titel vorhanden ist
            status = "Error"
            titel_und_jahr_elements = content.xpath("//div[@class='col-sm-12']/h1")
            if titel_und_jahr_elements:
                status = "OK"
                titel_und_jahr_text = titel_und_jahr_elements[0].text.strip()
                titel = re.sub(r'\s*\([^)]*\)', '', titel_und_jahr_text)
                self.Main.lnEdit_DBTitel.setText(titel)
            self.scrap_status("Titel", status)

    def movies_abfrage_iafd(self, content: html.Element, url: str) -> None:
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Movies","IAFD")         

        ### Release-Date Abfrage, Windows-Konform umwandeln ###
        movies_elements = content.xpath("//div[@id='appearssection']//a")

        if movies_elements:
            status = "OK" 
            movies_text = movies_elements[0].text.strip()
            tooltip_text = f"{quelle}: {movies_text}"
            titel = modified_title = re.sub(r'\s+\((\d{4})\)', r'(\1)', movies_text)            
            movies = f"Scene X: XXX-{titel}FULLHD-ENGLISH"
            self.set_daten_in_maske(maske_typ, feld, url, movies)                
            
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)    
        self.scrap_status(feld, status)

    def akas_abfrage_iafd(self, content: html.Element, url: str, studio: str) -> None:
        ### Alternativ Titel Abfragen und in Movies mit Performers reinpacken  ###
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Movies","IAFD")

        movies_elements = content.xpath("//div[@id='appearssection']//a")
        akas_elements = content.xpath("//dl[b[contains(., 'Also Known As')]]/dd | //dl[b[contains(., 'Alternate Versions:')]]/dd/a")

        movies: str = ""
        if movies_elements or akas_elements:
            tooltip_text = ""
        if movies_elements:
            status = "OK"  
            for movie_element in movies_elements:
                movies_text = movie_element.text.strip()
                tooltip_text += f"{quelle}: {movies_text}\n"
                titel = modified_title = re.sub(r'\s+\((\d{4})\)', r'(\1)', movies_text)            
                movies += f"Scene X: XXX-{titel}FULLHD-ENGLISH\n"
                
        if akas_elements:
            status = "OK, OK"
            tooltip_text += f"{quelle}: {len(akas_elements)} Alias Scene gefunden"
            
            performers_elements = content.xpath("//table[@class='table']//tr[last()]/td[@colspan='3']")
            performers_text = performers_elements[0].text.strip()
            serie = self.Main.lnEdit_DBSerie.text()
            if serie:
                status = "OK, OK, OK"
                serie = f"[{serie}]"
            for aka_element in akas_elements:                                
                aka=self.Main.windows_file_filter(re.sub("\(.*?\.com\)","",aka_element.text))
                movies += f"{studio} - {performers_text}-{aka}{serie}\n"
            self.set_daten_in_maske(maske_typ, feld, url, movies[:-1])
        
        self.set_tooltip_text(maske_typ, feld, tooltip_text[:-1], quelle)
        self.scrap_status(feld, status)

    def synopsis_abfrage_iafd(self, content: html.Element, url: str) -> None:     
        ### Beschreibung Abfrage ###
        status, maske_typ, feld, quelle, tooltip_text = self.initialisize_abfrage("Synopsis","IAFD")

        synopsis_element = content.xpath("//div[@id='synopsis']//li[1]")
        if synopsis_element:
            status = "OK"
            synopsis_text = synopsis_element[0].text
            tooltip_text = f"{quelle}: ({len(synopsis_text)}) -> '{synopsis_text[:40]}...'"            
            self.set_daten_in_maske(maske_typ, feld, url, synopsis_text)
        
        self.set_tooltip_text(maske_typ, feld, tooltip_text, quelle)          
        self.scrap_status(feld, status)

    def performers_abfrage_iafd(self, content: html.Element, url: str) -> None:
        ### Darsteller Abfrage incl Alias und Tätigkeit und dann in liste einfügen ###
        status: str = "Error"        

        performers_elements = content.xpath("//div[@class='castbox']")
        if performers_elements:            
            status = "OK"
            df_merge=self.IAFD_merge_DB(performers_elements)
            self.Main.tblWdg_Performers.setRowCount(len(df_merge)) 
            zeile=0      
            for zeile in range(len(df_merge)):
                for spalte in range(len(df_merge.columns)):
                    item = QTableWidgetItem(str(df_merge.iloc[zeile, spalte]))
                    self.Main.tblWdg_Performers.setItem(zeile, spalte, item)
        self.scrap_status("Performers", status)

    def minutes_to_hhmmss(self,minutes : int) -> str:
        hours, minutes = divmod(minutes, 60)        
        return f"{hours:02d}:{minutes:02d}:00"          

    def DB_Anzeige(self):
        self.Main.tblWdg_Daten.itemSelectionChanged.connect(self.select_whole_row) # aktiviert die komplette Zeile      
        hostname = self.Main.tblWdg_Daten.selectedItems()[1].text()
        for link in hostname.split("\n"):
            self.Main.model_database_weblinks.appendRow(QStandardItem(link))
        self.Main.set_studio_in_db_tab(hostname) 
        ### ----------- Perfomer incl rest in die TableWidget packen ------------ ###
        performs=self.Main.tblWdg_Daten.selectedItems()[3].text().split("\n")
        aliass=(self.Main.tblWdg_Daten.selectedItems()[4].text()+"\n"*len(performs)).split("\n")
        actions=(self.Main.tblWdg_Daten.selectedItems()[5].text()+"\n"*len(aliass)).split("\n")        
        for zeile,(db_performer,alias,action) in enumerate(zip(performs,aliass,actions)):              
            if " <--" in db_performer:
                action=db_performer[db_performer.find(" <--")+4:]
                db_performer=db_performer.replace(" <--"+action,"")
            if " (Credited: " in db_performer:
                alias=db_performer[db_performer.find(" (Credited: ")+12:].replace(")","")
                db_performer=db_performer.replace(" (Credited: "+alias+")","") 
            self.Main.tblWdg_Performers.setRowCount(zeile+1)
            self.Main.tblWdg_Performers.setItem(zeile,0,QTableWidgetItem(db_performer))
            self.Main.tblWdg_Performers.setItem(zeile,1,QTableWidgetItem(alias))
            self.Main.tblWdg_Performers.setItem(zeile,2,QTableWidgetItem(action.strip()))  
        ### ----------- Data Link in Maske packen ------------ ###
        db_websides=DB_WebSide() 
        data18_link=db_websides.hole_data18link_von_db(hostname,self.Main.Btn_logo_am_db_tab.toolTip())         
        if data18_link:
            self.Main.lnEdit_DBData18Link.textChanged.disconnect()  # deaktiven 
            self.set_daten_in_maske("lnEdit_DB", "Data18Link", "Datenbank", data18_link) 
            self.Main.lnEdit_DBData18Link.textChanged.connect(self.Main.Web_Data18_change) # aktiven
            self.Main.lbl_checkWeb_Data18URL.setText("Check OK !") 
        ### ----------- IAFD Link in Maske packen ------------ ###
        if self.Main.tblWdg_Daten.selectedItems()[2]:
            self.Main.lnEdit_DBIAFDLink.textChanged.disconnect() # deaktiven      
            self.set_daten_in_maske("lnEdit_DB", "IAFDLink", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[2].text()) 
            self.Main.lnEdit_DBIAFDLink.textChanged.connect(self.Main.Web_IAFD_change) # aktiven 
            self.Main.lbl_checkWeb_IAFDURL.setText("Check OK !")
        ### ----------- Rest in Maske packen ------------ ###
        self.set_daten_with_tooltip("lnEdit_DB", "Dauer", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[6].text())
        self.set_daten_with_tooltip("lnEdit_DB", "Release", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[7].text())
        self.set_daten_with_tooltip("lnEdit_DB", "ProDate", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[8].text())
        self.set_daten_with_tooltip("lnEdit_DB", "Serie", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[9].text())
        self.set_daten_with_tooltip("lnEdit_DB", "Regie", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[10].text())
        self.set_daten_with_tooltip("lnEdit_DB", "SceneCode", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[11].text())
        self.set_daten_with_tooltip("txtEdit_DB", "Movies", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[12].text())
        self.set_daten_with_tooltip("txtEdit_DB", "Synopsis", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[13].text())
        self.set_daten_with_tooltip("txtEdit_DB", "Tags", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[14].text())  

    def set_daten_with_tooltip(self, widget_typ: str, art: str, quelle: str, daten: str) -> None:
        tooltip_text = f"{quelle}: Kein Eintrag"
        if daten:
            anzahl = f"({len(daten)}) " if len(daten) > 30 else ""
            tooltip_text = f"{quelle}: {anzahl}-> {daten[:40]}"
            self.set_daten_in_maske(widget_typ, art, quelle, daten) 
        self.set_tooltip_text(widget_typ, art, tooltip_text, quelle)      

    def select_whole_row(self):
        selected_items = self.Main.tblWdg_Daten.selectedItems()
        if selected_items:
            # Mindestens ein Element ist ausgewählt, wir bestimmen die Zeilennummer
            row = self.Main.tblWdg_Daten.row(selected_items[0])
            # Anzahl der Spalten in Ihrer Tabelle
            column_count = self.Main.tblWdg_Daten.columnCount()

            # Erzeugen Sie einen Auswahlbereich für die gesamte Zeile
            selection = QTableWidgetSelectionRange(row, 0, row, column_count - 1)
            self.Main.tblWdg_Daten.setRangeSelected(selection, True)

    def set_daten_in_maske(self, widget: str, info_art: str, source: str, daten: str) -> None:
        if daten:         
            anzahl=self.Main.datenbank_save(info_art,source,daten)
            if widget=="lnEdit_DB":
                getattr(self.Main, f"{widget}{info_art}").setText(daten)
            else:
                getattr(self.Main, f"{widget}{info_art}").setPlainText(daten) 
                

    def set_tooltip_text(self, widget: str, info_art: str, tooltip_text: str, source: str) -> None:
        current_tooltip = getattr(self.Main, f"{widget}{info_art}").toolTip()
        tooltip_parts = current_tooltip.split("<br>") if current_tooltip else []

        if not any(source + ": " in item for item in tooltip_parts):            
            tooltip_parts.append(tooltip_text)
        new_tooltip = ("<br>".join(tooltip_parts))
        getattr(self.Main, f"{widget}{info_art}").setToolTip(new_tooltip)   


    def Copy_IAFD(self):
        ausgabe=""
        for zeile in range(self.tblWdg_Performers.rowCount()):
            alias,action=("","")
            if self.tblWdg_Performers.item(zeile, 1).text()!="":
                alias=" (Credited : "+self.tblWdg_Performers.item(zeile, 1).text()+") "
            if self.tblWdg_Performers.item(zeile, 2).text()!="":
                action=" <-- "+self.tblWdg_Performers.item(zeile, 2).text()
            ausgabe=ausgabe+"\n"+self.tblWdg_Performers.item(zeile, 0).text()+alias+action
        iafd=ausgabe[1:]+"\nScene Code: "+self.lnEdit_DBSceneCode.text()+"\nProduction Date: "+self.lnEdit_DBProDate.text()+("\nRegie: "+self.lnEdit_DBRegie.text() if self.lnEdit_DBRegie.text()!="" else "")
        self.txtEdit_Clipboard.setPlainText(iafd)
        pyperclip.copy(iafd)  
    
    def WebSideLink_update(self,studio: str) -> None:        
        tag: str="" 
        response = requests.get(studio, headers=HEADERS)
        
        db_webside = DB_WebSide()
        synopsis, tags = db_webside.hole_movie_infos_from_artist_Tags(studio)
        synopsis_text_element = html.fromstring(response.content).xpath("//div[@class='sc-xz1bz0-0 lgrCSo']/p/text()")
        tags_text_element = html.fromstring(response.content).xpath("//div[@class='sc-xz1bz0-0 lgrCSo']//a/text()")        
        
        if len(synopsis_text_element)==1:            
            self.txtEdit_DBSynopsis.setText(synopsis_text_element[0].replace('"','\''))           
        if len(tags)>1:
            for tag_element in tags_text_element:
                tag=tag+";"+tag_element.title().replace("Shaved","Shaved Pussy")
            self.txtEdit_DBTags.setText(tag[1:])        

    def data18Link_update(self):        
        data18_link=self.lnEdit_DBData18Link.text()
        pyperclip.copy(data18_link)
        self.txtEdit_Clipboard.setPlainText(data18_link)
     

    def IAFD_merge_DB(self, performers: WebElement) -> pd.DataFrame: # Panda-Dataframe
        data: list = []        
        for row in range(self.Main.tblWdg_Performers.rowCount()):
            name = self.Main.tblWdg_Performers.item(row, 0).text() 
            if name == "":
                continue            
            alias = self.Main.tblWdg_Performers.item(row, 1).text() if self.Main.tblWdg_Performers.item(row, 1) else ""
            action = self.Main.tblWdg_Performers.item(row, 2).text() if self.Main.tblWdg_Performers.item(row, 2) else ""
            data.append({'Name': name, 'Alias': alias, 'Action': action})
        df_db = pd.DataFrame(data)

        # Laden Sie Daten aus der Internetquelle (IAFD) in ein weiteres DataFrame        
        for performer in performers:
            name = performer.xpath(".//a/text()")[0]
            credited_element = performer.xpath(".//i")[0] if performer.xpath(".//i") else None
            credited = credited_element.xpath("normalize-space(text())").replace("(Credited: ","").replace(")","") if credited_element is not None else ""
            
            skill_element = performer.xpath(".//br/following-sibling::text()[normalize-space()]")
            skill = skill_element[1].strip() if skill_element[1] is not None else ""
            data.append({'Name': name, 'Alias': credited, 'Action': skill})
        df_IAFD = pd.DataFrame(data)
        # Kombinieren Sie beide DataFrames und entfernen Sie doppelte Einträge
        df_merged = pd.concat([df_db, df_IAFD], ignore_index=True)
        df_merged = df_merged.groupby('Name').agg({'Alias': 'first', 'Action': ' '.join}).reset_index()                
        # Entfernen Sie doppelte Einträge nach der Spalte 'Name'
        df_merged.drop_duplicates(subset=['Name'], inplace=True)
        # doppelte einträge in Action löschen        
        merge_action: list = []
        for action in df_merged['Action']:
            words = action.split()            
            merge_action.append(' '.join(list(set(words))))
        # Ersetzen Sie die 'Action'-Spalte durch die bereinigten Daten    
        df_merged['Action'] = merge_action 
        # Alias = Name aus Eintrag löschen
        df_merged = df_merged[~df_merged['Name'].isin(df_merged["Alias"])]
        return df_merged

    def AddPerformers(self):
        self.tblWdg_Performers.setRowCount(self.tblWdg_Performers.rowCount()+1) 
        self.tblWdg_Performers.setItem(self.tblWdg_Performers.rowCount()-1,0,QTableWidgetItem(""))
        self.tblWdg_Performers.setItem(self.tblWdg_Performers.rowCount()-1,1,QTableWidgetItem(""))       
        self.tblWdg_Performers.setItem(self.tblWdg_Performers.rowCount()-1,2,QTableWidgetItem(""))
        self.tblWdg_Performers.setCurrentCell(self.tblWdg_Performers.rowCount()-1, 0)

    # Darsteller usw. der Reihe nach in die Datenbank vorbereiten   
    def get_videodata_from_ui(self, performers: str, alias: str, actions: str) -> dict:
        daten_satz = {
        "Titel": self.Main.lnEdit_DBTitel.text(),
        "IAFDLink": self.Main.lnEdit_DBIAFDLink.text(),
        "Data18Link": self.Main.lnEdit_DBData18Link.text(),
        "Performers": performers,
        "Alias": alias,
        "Action": actions,
        "ReleaseDate": self.Main.lnEdit_DBRelease.text(),
        "Dauer": self.Main.lnEdit_DBDauer.text(),
        "SceneCode": self.Main.lnEdit_DBSceneCode.text(),
        "Synopsis": self.Main.txtEdit_DBSynopsis.toPlainText(),
        "Tags": self.Main.txtEdit_DBTags.toPlainText(),
        "Serie": self.Main.lnEdit_DBSerie.text(),
        "ProDate": self.Main.lnEdit_DBProDate.text(),
        "Regie": self.Main.lnEdit_DBRegie.text(),
        "Movies": self.Main.txtEdit_DBMovies.toPlainText(),                
                    }
        return daten_satz
    
    
    def get_performers_from_ui(self) -> Tuple[str, str, str]:
        performers, alias, actions = "", "", ""
        
        for zeile in range(self.Main.tblWdg_Performers.rowCount()):
            row_data = [self.Main.tblWdg_Performers.item(zeile, col).text() for col in range(3)]
            performers += row_data[0] + "\n"
            alias += row_data[1] + "\n"
            actions += row_data[2] + "\n"
        
        return performers.strip("\n"), alias.strip("\n"), actions.strip("\n")

     
    # Datensatz updaten 
    def update_db_and_ui(self, studio: str, WebSideLink: str) -> None:
        performers, alias, actions = self.get_performers_from_ui()
        video_data = self.get_videodata_from_ui(performers, alias, actions)
        db_webside = DB_WebSide(self.Main)
        if not studio: 
            self.show_error_message("Kein Studio angegeben !") 
            self.clean_label()           
            return
        errorview, neu = db_webside.update_videodaten_in_db(studio, WebSideLink, video_data)
        
        if errorview:
            if errorview == "Link nicht gefunden !":
                result = MsgBox(self.Main, f"{errorview} - Soll der Datensatz neu angelegt werden ?","q")
                if result == QMessageBox.StandardButton.Yes:
                    errview , farbe, isneu = db_webside.add_neue_videodaten_in_db(self, studio, WebSideLink, video_data)  
                    if isneu == 1:
                        self.show_success_message(f"{neu} Datensatz wurde in {studio} gespeichert (update)!",f"{neu} Datensatz geaddet")                          
            self.show_error_message(errorview)               
        else:
            if neu:
                self.show_success_message(f"{neu} Datensatz wurde in {studio} gespeichert (update)!",f"{neu} Datensatz aktualisiert")                

                db_webside = DB_WebSide(self.Main)
                errorview = db_webside.hole_link_aus_db(WebSideLink, studio)
                if not errorview:
                    self.Main.tabelle_erstellen()
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
        db_webside_settings = Webside_Settings(self.Main)
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
    Infos_WebSides()