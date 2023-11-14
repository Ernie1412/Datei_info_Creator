from PyQt6.QtWidgets import QTableWidgetItem, QApplication, QMessageBox
from PyQt6.QtGui import QColor, QBrush

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, TimeoutException

import requests
from lxml import html
from itertools import zip_longest
import re
from time import sleep
from datetime import datetime
from typing import Tuple, Union

from utils.database_settings import Webside_Settings, DB_WebSide 

from config import HEADERS, selenium_browser_check

class VideoUpdater:
    def __init__(self, baselink: str = None, studio: str = None, MainWindow = None):        
        self.Main = MainWindow    
        self.baselink: str = baselink
        self.studio: str = studio
        self.zeile: int = 0
        self.start_clicks: str = None                

    def get_scrap_settings_from_db(self) -> Tuple [str, int]:
        # Initialisierung und Konfiguration hier        
        driver: WebDriver = None       
        db_website_settings = Webside_Settings()
        errorview, video_data = db_website_settings.get_videodatas_from_baselink(self.baselink)
        if errorview:
            self.Main.MsgBox(f"Fehler beim Holen der {self.baselink} mit dem Fehler: {errorview}","w")
            return
        self.baselink = video_data.get_data()["Homepage"]
        first_page_url = video_data.get_data()["Homepage"] + video_data.get_data()["Video_page"]
        if video_data.get_data()["Click"]:
            self.start_clicks = video_data.get_data()["Click"]            
            errorview, content, driver = self.open_url_javascript(first_page_url.format(zahl=1), self.start_click)
        else:
            errorview, content = self.open_url_no_javascript(first_page_url.format(zahl=1))
        
        first_page = self.Main.spinBox_vonVideo.value()
        last_page = self.Main.spinBox_bisVideo.value() 
        page=1        
        while page <= last_page:                        
            self.Main.lbl_DatenSatz.setText(str(page))
            self.Main.lbl_DatenSatz.repaint()
            page_url = first_page_url.format(zahl=page) # fügt eine neue Websidezahl hinzu            
            if driver:            
                errorview, content, driver = self.open_url_javascript(page_url)
            else:
                errorview, content = self.open_url_no_javascript(page_url)
            page += 1   
            if errorview: 
                page = last_page
            self.hole_video_data(content, driver, video_data)             
        
        if driver:    
            driver.close()
        return errorview, self.zeile
    
    def hole_video_data(self, content, driver, video_data):        
        # Daten aus dem Baum extrahieren
        link_elements = content.xpath(video_data.get_data()["Link_XPath"]) if video_data.get_data()["Link_XPath"] else ""
        titel_elements = content.xpath(video_data.get_data()["Titel_XPath"]) if video_data.get_data()["Titel_XPath"] else "" 
        datum_elements = content.xpath(video_data.get_data()["ReleaseDate_xpath"]) if video_data.get_data()["ReleaseDate_xpath"] else ""
        zeit_elements = content.xpath(video_data.get_data()["Dauer"]) if video_data.get_data()["Dauer"] else "" 
        code_elements = content.xpath(video_data.get_data()["SceneCode"]) if video_data.get_data()["SceneCode"] else ""

        num_retries: int = 0
        max_retries: int = 5 # keine neuen daten, nach 5 Versuchen !
        neu: int = 0
        dauer: str = None 
        scene_code: str = None
        datum: str = None

        while num_retries < max_retries and any(zip_longest(link_elements, titel_elements, datum_elements, zeit_elements, code_elements, fillvalue='')):

            elements = next(zip_longest(link_elements, titel_elements, datum_elements, zeit_elements, code_elements, fillvalue=''))
            link = elements[0].get("href") if elements[0].get("href").startswith("https://") else self.baselink[:-1] + elements[0].get("href")                     
            titel = elements[1].get("title").title().strip() if video_data.get_data()["Titel_Gross"] else elements[1].get("title").strip()
            if elements[2] != "":
                datum = self.datum_umwandeln(elements[2].text.strip(), video_data.get_data()["ReleaseDate_Format"])
            if elements[3] != "":
                dauer = re.search(r'\d{1,2}:\d+(:\d+)?', elements[3].text).group() if re.search(r'\d{1,2}:\d+(:\d+)?', elements[3].text) else None
            if elements[4] != "":
                scene_code = elements[4].text.replace("video-","").upper() 

            beschreibung, stars, tags, serie, dauer, datum = self.hole_link_infos(link, driver, dauer, datum)            

            item_data = [titel, link, "", "", datum, dauer, scene_code, beschreibung, stars, "", "", tags, serie, self.studio]
            replay, farbe, isneu = self.add_in_database(item_data)
            if replay:
                break            
            if isneu:
                num_retries = 0
                neu += 1                
            else:
                num_retries += 1
            self.ausgabe_der_daten_in_ui(item_data, farbe)
        #     yield elements  # Daten als Generator zurückgeben

    # mit Selenium scrapen, weil javascript aktiv
    def open_url_javascript(self, url: str, start_click: str = None) -> Union [str, WebElement, WebDriver]:        
        errorview: str = None          
        driver, status = selenium_browser_check()
        driver.maximize_window()  
        driver.get(url)
        content = html.fromstring(driver.page_source)        

        if self.start_clicks:
            for start_click in self.start_clicks.split("\r\n"):
                try:
                    elem = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, start_click)))
                except (TimeoutError, NoSuchElementException) as e:
                    self.Main.MsgBox(f"Fehler beim Öffen der {url} mit dem Fehler: {e}","w")
                    errorview = e
                else:                    
                    driver.execute_script("arguments[0].click();",elem)
                    sleep(1)
        # scroll_steps = 10  # Anzahl der Schritte
        # scroll_duration = 1  # Dauer pro Schritt in Sekunden

        # # Langsames Scrollen durchführen
        # for _ in range(scroll_steps):
        #     # JavaScript ausführen, um um eine Seite nach unten zu scrollen
        #     driver.execute_script("window.scrollBy(0, window.innerHeight);")
            
        #     # Kurze Wartezeit zwischen den Schritten, um das Scrollen sichtbar zu machen
        #     sleep(scroll_duration)
                             
        return errorview, content, driver 

    # mit requests/lxml scrapen, kein javascript und schnell
    def open_url_no_javascript(self, url: str, start_click: str = None) -> Union [str, html.Element]:
        errorview = None
        content = None
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.Main.MsgBox(f"Fehler beim Öffen der {url} mit dem Fehler: {e}","w")
            errorview = e
        else:
            content = html.fromstring(response.content)
        return errorview, content  
    

    def add_in_database(self, item_data: list) -> Tuple [str, str, int]:
        replay: QMessageBox = None                 
        # Verarbeiten und in die Datenbank einfügen
        db_webside = DB_WebSide()
        errorview, farbe, isneu = db_webside.add_neue_videodaten_in_db(item_data)
        if errorview:
            replay = self.Main.MsgBox(f"Fehler beim Datenbank adden mit dem Fehler: {errorview}\nAbbruch ?","q")
            if replay == QMessageBox.Yes:
                return replay, farbe, isneu
        return replay, farbe, isneu

    
    def ausgabe_der_daten_in_ui(self, item_data: list, farbe: str) -> None:
        self.Main.tblWdg_Daten.setRowCount(self.zeile)
        item = QTableWidgetItem(item_data.titel)
        item.setBackground(QBrush(QColor(farbe)))
        self.Main.tblWdg_Daten.setItem(self.zeile-1,0,item)
        item = QTableWidgetItem(item_data.link)
        item.setBackground(QBrush(QColor(farbe)))
        self.Main.tblWdg_Daten.setItem(self.zeile-1,1,item)
        self.Main.tblWdg_Daten.verticalScrollBar().setValue(self.zaehler) 
        self.Main.tblWdg_Daten.resizeColumnsToContents()
        self.Main.tblWdg_Daten.scrollToBottom()
        self.Main.lbl_DatenSatz.setText(str(self.zeile))               
        QApplication.processEvents()
        self.zeile+=1   

                             
    def hole_link_infos(self, link: str, driver: WebDriver, dauer: str, datum: str) -> Tuple[str, str, str, str, str, str]:        
        if driver:            
            errorview, content, driver = self.open_url_javascript(link)
        else:
            errorview, content = self.open_url_no_javascript(link)
        if errorview: 
            return "", "", "", "", dauer, datum    # 6 x str = ""

        beschreibung = self.hole_beschreibung_xpath_settings(content, driver, link) # collaps button ?
        tags = self.hole_tags_xpath_settings(content, driver, link) # collaps button ?
        datum = self.hole_datum_xpath_settings(content, datum)
        stars = self.hole_performers_xpath_settings(content)        
        serie = self.hole_serie_xpath_settings(content)
        dauer = self.hole_dauer_xpath_settings(content, dauer)
        
        return beschreibung, stars, tags, serie, dauer, datum   
    
    def hole_beschreibung_xpath_settings(self, content, driver, link) -> str:
    # Code zum Extrahieren der Beschreibung        
        beschreibung = None
        db_settings = Webside_Settings()        

        errview, xpath_synopsis, xpath_synopsis_attri, xpath_synopsis_clicks = db_settings.get_movie_settings_for_beschreibung(self.baselink)
        if not errview and xpath_synopsis:
            if xpath_synopsis_clicks:
                if not driver:
                    errorview, content, driver = self.open_url_javascript(link)                    

                beschreibung = content.xpath(xpath_synopsis) or beschreibung

                if not beschreibung:
                    try:
                        elem = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, xpath_synopsis_clicks)))
                        driver.execute_script("arguments[0].click();", elem)
                        beschreibung = content.xpath(xpath_synopsis)
                    except NoSuchElementException:
                        pass

        return beschreibung[0].text if beschreibung else ""
    
    def hole_tags_xpath_settings(self, content, driver, link) -> str:
        tags: str = None
        tags_elements: list = []
        db_settings = Webside_Settings()              

        errview, xpath_tags, xpath_tags_attri, xpath_tags_click = db_settings.get_movie_settings_for_tags(self.baselink)
        if not errview and xpath_tags:
            if xpath_tags_click:
                if not driver:
                    errorview, content, driver = self.open_url_javascript(link)

                tags_elements = content.xpath(xpath_tags) or tags_elements

                if not tags_elements:
                    try:
                        elem = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, xpath_tags_click)))
                        driver.execute_script("arguments[0].click();", elem)
                        tags_elements = content.xpath(xpath_tags)
                    except NoSuchElementException:
                        return tags                
                tags = ";".join(tag.text.title().strip() for tag in tags_elements)
        return tags
    
    # wenn noch kein datum da ist dann datum aus javascript-element holen und in richtigen Format umwandeln
    def hole_datum_xpath_settings(self, content, datum: str) -> str:        
        db_settings = Webside_Settings()        

        errview, xpath_datum, datum_format = db_settings.get_movie_settings_for_erstelldatum(self.baselink)

        if not datum and not errview and xpath_datum: 
            datum_text = content.xpath(xpath_datum)[0].text.strip() if content.xpath(xpath_datum) else None            
            datum = self.datum_umwandeln(datum_text, datum_format)
        return datum
    
    ### Dauer, wenn noch nicht da ist ###
    def hole_dauer_xpath_settings(self, content, dauer: str) -> str: 
        db_settings = Webside_Settings()  

        errview, xpath_dauer = db_settings.get_movie_settings_for_dauer(self.baselink)
        
        if not dauer and not errview and xpath_dauer:            
            dauer_text = content.xpath(xpath_dauer)[0].text.strip() if content.xpath(xpath_dauer) else None
            dauer = self.time_format_00_00_00(dauer_text)
        return dauer
    
    ### Performers, Artists, Stars ###
    def hole_performers_xpath_settings(self, content) -> str:
        stars: str = None 
        db_settings = Webside_Settings()

        errview, xpath_performers, xpath_performers_gross = db_settings.get_movie_settings_for_artist(self.baselink)
        
        if not errview and xpath_performers:
            stars_elements = content.xpath(xpath_performers) if content.xpath(xpath_performers) else None
            if stars_elements:
                stars = "\n".join(star.text.strip() for star in stars_elements)
                if xpath_performers_gross:
                    stars = stars.title()
        return stars  
    
    ### Serie, NebenSide ###
    def hole_serie_xpath_settings(self, content) -> str:
        serie: str = None
        db_settings = Webside_Settings()
        errview, xpath_serie = db_settings.get_movie_settings_for_nebenside(self.baselink)        
        
        if not errview and xpath_serie:
            serie_element = content.xpath(xpath_serie)[0].text.strip() if content.xpath(xpath_serie) else None              
            serie = serie_element.title() if " " in serie_element else serie_element
        return serie 
    

    def time_format_00_00_00(self, text: str) -> str:
        hh_mm_ss = None 
        match = re.search(r'(\d+:\d+:\d+|\d+:\d+)', text)
        if match:
            duration = f"00:{match.group(1)}"  # Extrahierte Zeit
            # Falls erforderlich, in das Format "00:00:00" konvertieren
            hh_mm = list(reversed(duration.split(":")))   
            hh_mm_ss = f"{int(hh_mm[2]):02}:{int(hh_mm[1]):02}:{int(hh_mm[0]):02}"
        else:
            hh_mm_ss = None
        return hh_mm_ss
    
    def datum_umwandeln(self, date_str:str, date_format: str) -> str:
        try:
            date_obj = datetime.strptime(date_str, date_format)
        except ValueError:
            return None    
        # Datumsobjekt in das gewünschte Format umwandeln        
        return date_obj.strftime('%Y.%m.%d %H:%M:%S')