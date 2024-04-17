from PyQt6.QtWidgets import QTableWidgetItem

import requests
from lxml import html
from selenium.webdriver.remote.webelement import WebElement

import re
from datetime import datetime
import pandas as pd

from utils.helpers.check_biowebsite_status import CheckBioWebsiteStatus
from gui.helpers.set_tootip_text import SetTooltipText, SetDatenInMaske
from utils.database_settings.database_for_settings import Webside_Settings
from utils.helpers.umwandeln import time_format_00_00_00

from config import HEADERS

class ScrapeIAFDScene():          
    #### --------------------------------------------------------------------------------------- ####
    def __init__(self, MainWindow):
            
        super().__init__() 
        self.Main = MainWindow    
    def Web_IAFD_change(self):
        check_status = CheckBioWebsiteStatus(self.Main)
        webdatabase: str="IAFD"

        check_status.just_checking_labelshow(webdatabase) 
        if self.Main.lnEdit_DBIAFDLink.text().startswith("https://www.iafd.com/title"):                    
            response = requests.get(self.Main.lnEdit_DBIAFDLink.text(), headers=HEADERS)                
            if len(html.fromstring(response.content).xpath('//div[@class="col-sm-12"]/h1/text()'))==1:
                check_status.check_OK_labelshow(webdatabase)
            else:
                check_status.check_negativ_labelshow(webdatabase)  
        else:
            self.Main.lnEdit_IAFD_titel.setText(self.Main.lnEdit_DBTitel.text())
            self.Main.lnEdit_db_jahr.setText(self.Main.lnEdit_DBRelease.text()[:4])
            self.Main.stackedWidget.setCurrentIndex(3)
            check_status.check_error_labelshow(webdatabase)

    def webscrap_iafd(self):
        check_status = CheckBioWebsiteStatus(self.Main)
        check_status.check_loading_labelshow("IAFD")
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
        if self.Main.lnEdit_DBTitel.text() and self.Main.tblWdg_files.currentColumn() != -1:
            self.Main.Btn_Speichern.setEnabled(True)        
        check_status.check_loaded_labelshow("IAFD")

    def open_url_no_javascript(self, url: str) -> html.Element: 
        check_status = CheckBioWebsiteStatus(self.Main)
        status: str = "Error"
        response: str = None
        content: str = None                     
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            check_status.fehler_ausgabe_checkweb(e,"IAFD") 
            status = e           
        else:
            status = "OK"
            content = html.fromstring(response.content)
        check_status.scrap_status(f"{url} wird geöffnet", status)
        return content      

    def regie_abfrage_iafd(self, content: html.Element, url):
        check_status = CheckBioWebsiteStatus(self.Main)        
        ### Regie Abfrage ###  
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Regie","IAFD")        

        regie_element = content.xpath("//p[contains(string(),'Director')]/following::p[1]/text() \
                                     | //p[contains(string(),'Director')]/following::p[1]/a/text()\
                                     | //p[contains(string(),'Directors')]/following::p[1]/a/text()")
        if regie_element:
            tooltip_text = f"{quelle}: {regie_element[0]}"
            status = "OK"
            if regie_element[0] != "No Director Credited" and regie_element[0] != "No Data": 
                SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, regie_element[0])

        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        check_status.scrap_status(feld, status)

    def dauer_abfrage_iafd(self, content: html.Element, url):
        check_status = CheckBioWebsiteStatus(self.Main)
        ### die Runtime Abfrage, Sekunden mit :00 auffüllen ###
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Dauer","IAFD")        

        dauer = content.xpath("//p[contains(.,'Minutes')]/following::p[1]/text()")        
        if dauer: 
            status ="OK"
            tooltip_text = f"{quelle}: {dauer[0]}"
            if dauer[0] != "No Data":
                dauer = time_format_00_00_00(f"{dauer[0]}:00")
                SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, dauer)

        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        check_status.scrap_status(feld, status)

    def serie_abfrage_iafd(self, content: html.Element, url: str) -> str:
        check_status = CheckBioWebsiteStatus(self.Main)
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Serie","IAFD")                
        studio = None
        ### Studio und Serie, falls vorhanden Abfrage ###
        studio_element = content.xpath("//p[contains(.,'Studio')]/following::p[1]/a")
        if studio_element:
            status = "OK"            
            tooltip_text = f"{quelle}: {studio_element[0].text}"
            db_webside_settings = Webside_Settings(MainWindow=self.Main)
            studio, serie = db_webside_settings.from_studio_to_subside_for_iafd(studio_element[0].text)            
            SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, serie)            

        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        check_status.scrap_status(feld, status)
        return studio
    

    def releasedate_abfrage_iafd(self, content: html.Element, url: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Release","IAFD")         

        ### Release-Date Abfrage, Windows-Konform umwandeln ###
        release_date_elements = content.xpath("//p[contains(.,'Release Date')]/following::p[1]")

        if release_date_elements:
            status = "OK" 
            release_text = release_date_elements[0].text.strip()
            tooltip_text = f"{quelle}: {release_text}"
            if "no data" not in release_text.lower():
                release_date = datetime.strptime(release_text, "%b %d, %Y").strftime("%Y:%m:%d %H:%M:%S")
                SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, release_date)                
            
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        check_status.scrap_status(feld, status)

    def titel_abfrage_iafd(self, content: html.Element, url: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)
        ### Titel Abfrage, das Jahr "(2023)" cutten ###
        if self.Main.lnEdit_DBTitel.text() == "": ## wenn kein Titel vorhanden ist
            status = "Error"
            titel_und_jahr_elements = content.xpath("//div[@class='col-sm-12']/h1")
            if titel_und_jahr_elements:
                status = "OK"
                titel_und_jahr_text = titel_und_jahr_elements[0].text.strip()
                titel = re.sub(r'\s*\([^)]*\)', '', titel_und_jahr_text)
                self.Main.lnEdit_DBTitel.setText(titel)
            check_status.scrap_status("Titel", status)

    def movies_abfrage_iafd(self, content: html.Element, url: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Movies","IAFD")         

        ### Release-Date Abfrage, Windows-Konform umwandeln ###
        movies_elements = content.xpath("//div[@id='appearssection']//a")

        if movies_elements:
            status = "OK" 
            movies_text = movies_elements[0].text.strip()
            tooltip_text = f"{quelle}: {movies_text}"
            titel = modified_title = re.sub(r'\s+\((\d{4})\)', r'(\1)', movies_text)            
            movies = f"Scene X: XXX-{titel}FULLHD-ENGLISH"
            SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, movies)                
            
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)    
        check_status.scrap_status(feld, status)

    def akas_abfrage_iafd(self, content: html.Element, url: str, studio: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)
        ### Alternativ Titel Abfragen und in Movies mit Performers reinpacken  ###
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Movies","IAFD")

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
            SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, movies[:-1])
        
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text[:-1], quelle)
        check_status.scrap_status(feld, status)

    def synopsis_abfrage_iafd(self, content: html.Element, url: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)     
        ### Beschreibung Abfrage ###
        status, maske_typ, feld, quelle, tooltip_text = check_status.initialisize_abfrage("Synopsis","IAFD")

        synopsis_element = content.xpath("//div[@id='synopsis']//li[1]")
        if synopsis_element:
            status = "OK"
            synopsis_text = synopsis_element[0].text
            tooltip_text = f"{quelle}: ({len(synopsis_text)}) -> '{synopsis_text[:40]}...'"            
            SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, synopsis_text)
        
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)          
        check_status.scrap_status(feld, status)

    def performers_abfrage_iafd(self, content: html.Element, url: str) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)
        ### Darsteller Abfrage incl Alias und Tätigkeit und dann in liste einfügen ###
        status: str = "Error"        

        performers_elements = content.xpath("//div[@class='castbox']")
        if performers_elements:            
            status = "OK"
            df_merge=self.IAFD_merge_DB(performers_elements)
            self.Main.tblWdg_DB_performers.setRowCount(len(df_merge)) 
            zeile=0      
            for zeile in range(len(df_merge)):
                for spalte in range(len(df_merge.columns)):
                    item = QTableWidgetItem(str(df_merge.iloc[zeile, spalte]))
                    self.Main.tblWdg_DB_performers.setItem(zeile, spalte, item)
        check_status.scrap_status("Performers", status)

    def IAFD_merge_DB(self, performers: WebElement) -> pd.DataFrame: # Panda-Dataframe
        data: list = []        
        for row in range(self.Main.tblWdg_DB_performers.rowCount()):
            name = self.Main.tblWdg_DB_performers.item(row, 0).text() 
            if name == "":
                continue            
            alias = self.Main.tblWdg_DB_performers.item(row, 1).text() if self.Main.tblWdg_DB_performers.item(row, 1) else ""
            action = self.Main.tblWdg_DB_performers.item(row, 2).text() if self.Main.tblWdg_DB_performers.item(row, 2) else ""
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