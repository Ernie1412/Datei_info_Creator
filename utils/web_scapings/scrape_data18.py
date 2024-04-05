from PyQt6.QtGui import QStandardItem

import re

from playwright.sync_api import sync_playwright, TimeoutError

from utils.helpers.check_biowebsite_status import CheckBioWebsiteStatus
from utils.helpers.scrapy_pipeline_settings import ScapyPipelineSettings
from gui.helpers.set_tootip_text import SetTooltipText, SetDatenInMaske
from utils.helpers.umwandeln import time_format_00_00_00, datum_umwandeln

class ScrapeData18(): 
    
    def __init__(self, MainWindow):            
        super().__init__() 
        self.Main = MainWindow
        
    def Web_Data18_change(self):
        check_status = CheckBioWebsiteStatus(self.Main)
        webdatabase: str="Data18"
        check_status.just_checking_labelshow(webdatabase)                      
        if self.Main.lnEdit_DBData18Link.text().startswith("https://www.data18.com/"):                         
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                url = self.Main.lnEdit_DBData18Link.text() 
                try:
                    page.goto(url, timeout=5000)
                except TimeoutError as e:
                    check_status.fehler_ausgabe_checkweb(e,"Data18URL") 
                    check_status.check_negativ_labelshow(webdatabase)                     
                else:
                    check_status.check_OK_labelshow(webdatabase)                
                finally:
                    browser.close()
        else:
            check_status.check_error_labelshow(webdatabase) 

    def webscrap_data18(self):
        check_status = CheckBioWebsiteStatus(self.Main)
        check_status.check_loading_labelshow("Data18")              
        url = self.Main.lnEdit_DBData18Link.text()
        felder = ["Release", "Dauer", "Serie", "Synopsis", "Movies", "QuellSide"]
        self.abfragen_data18(url, felder)
        check_status.check_loaded_labelshow("Data18")               

    def abfragen_data18(self, url: str, felder: list) -> None:
        check_status = CheckBioWebsiteStatus(self.Main)
        pipeline_settings = ScapyPipelineSettings(self.Main)
        self.Main.txtEdit_Clipboard.setPlainText("Scraping Data18 Element:")         
        status: str="Error"
        orginal_page: str=None 
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()            
            time_out = 2000                            
            try:
                page.goto(url, timeout=5000)
                if page.locator("//button[contains(string(),'ENTER - data18.com')]").is_visible():
                    page.locator("//button[contains(string(),'ENTER - data18.com')]").click() 
                else:   
                    page.locator('//span[@class="gen12"]/b/following::a[1]/b')                             
            except TimeoutError as e:
                check_status.fehler_ausgabe_checkweb(e,"Data18")
                check_status.scrap_status("URL Loading...", "Timeout Error: 5000ms")  
            else:
                check_status.scrap_status("URL Loading...", "OK") 
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
                        check_status.scrap_status(feld, status)
                    elif feld == "Serie": 
                        try:
                            serie_ele = page.locator("//p[contains(., 'Network') or contains(., 'Webserie')]/a[@class='bold']")
                            serie_text = serie_ele.nth(0).inner_text() 
                        except (TimeoutError, AttributeError):
                            status = f"Keine Serie/Sub-Side gefunden - Timeout: {time_out}ms"                       
                        else:
                            status = "OK" 
                            self.serie_abfrage_data18(serie_text, url) 
                        check_status.scrap_status(feld, status)                            
                    elif feld == "Synopsis":
                        try:
                            synopsis_text = page.locator("//div[@class='gen12']/div[starts-with(string(),'Story')]").inner_text()                             
                        except (TimeoutError, AttributeError):
                            status = f"Keine Synopsis gefunden - Timeout: {time_out}ms" 
                        else:
                            status = "OK"                                                         
                            self.synopsis_abfrage_data18(synopsis_text, url)
                        check_status.scrap_status(feld, status) 
                    elif feld == "Movies":                        
                        try:
                            movie_element = page.locator("//p/b[contains(.,'Movie')]/following::a[1]")                           
                            movie_text = movie_element.inner_text().replace("#","") 
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
                                studio_texts = pipeline_settings.pipeline_movie_distr(links, jahr)
                                self.movies_abfrage_data18(movie_text, scene_text, studio_texts, jahr, url) 
                        check_status.scrap_status(feld, status)
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
                                next_url = re.search(r'^(.*?)\?([^\?&]{1,10})=', current_url).group(1) if re.search(r'^(.*?)\?([^\?&]{1,10})=', current_url) else ""
                                urls = pipeline_settings.pipeline_add_link(next_url)                                
                                for url in urls.split("\n"):
                                    if not self.is_url_in_model(url):
                                        self.Main.model_database_weblinks.appendRow(QStandardItem(url))
                        check_status.scrap_status(feld, status)
            finally:
                browser.close()       
    
    def is_url_in_model(self, url):
        for row in range(self.Main.model_database_weblinks.rowCount()):
            item = self.Main.model_database_weblinks.item(row)
            if item is not None and item.text() == url:
                return True
        return False

    def release_abfrage_data18(self, release_text, url):
        status, maske_typ, feld, quelle, tooltip_text = CheckBioWebsiteStatus(self.Main).initialisize_abfrage("Release","Data18") 
        status = "OK"                    
        tooltip_text = f"{quelle}: ({len(release_text)}) -> {release_text}" 
        release_date = datum_umwandeln(release_text, "%B %d, %Y")             
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, release_date)        
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)        

    def dauer_abfrage_data18(self, dauer_text: str, url: str) -> None:
        ### die Runtime Abfrage ###
        status, maske_typ, feld, quelle, tooltip_text = CheckBioWebsiteStatus(self.Main).initialisize_abfrage("Dauer","Data18")
        if "Membership Site: " in dauer_text:
            membership_start = dauer_text.find("Membership Site: ") + 17
            dauer_text = dauer_text[membership_start:]
        dauer_text = time_format_00_00_00(dauer_text)
        tooltip_text = f"{quelle}: -> {dauer_text}"
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, dauer_text)
        
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)           

    def serie_abfrage_data18(self, serie_text: str, url: str) -> None:
        ### Abfrage nach Nebenside bzw Serie ### 
        status, maske_typ, feld, quelle, tooltip_text = CheckBioWebsiteStatus(self.Main).initialisize_abfrage("Serie","Data18")        
            
        serie_text = serie_text.title() if " " in serie_text else serie_text        
        serie_text = re.sub(r"\'[A-Z]", lambda match: "'" + match.group(0)[-1].lower(), serie_text)
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, serie_text)
        tooltip_text = f"{quelle}: -> {serie_text}"
        
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)        

    def movies_abfrage_data18(self, movie_text: str, scene_text: str, studio_texts: list, jahr: int, url: str) -> None:
        ### Abfrage nach möglichen Film-Release ###
        status, maske_typ, feld, quelle, tooltip_text = CheckBioWebsiteStatus(self.Main).initialisize_abfrage("Movies","Data18")         
                    
        scene_text = re.search(r'Scene \d+', scene_text).group() if re.search(r'Scene \d+', scene_text) else "Scene N/A"                     
        studio_text = studio_texts[0].replace(" ","")      

        tooltip_text = f"{quelle}: -> {movie_text}"
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, f"{scene_text}: {studio_text} - {movie_text}({jahr})FULLHD-ENGLISH") 
        
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        return status

    def synopsis_abfrage_data18(self, synopsis_text: str, url: str) -> None:
        ### Abfrage nach einer Beschreibung ### 
        status, maske_typ, feld, quelle, tooltip_text = CheckBioWebsiteStatus(self.Main).initialisize_abfrage("Synopsis","Data18")        
                   
        tooltip_text = f"{quelle}: ({len(synopsis_text[8:])}) -> {synopsis_text[8:40]}"
        SetDatenInMaske(self.Main).set_daten_in_maske(maske_typ, feld, url, synopsis_text[8:].replace("�",'').replace("\xa0", " "))
        
        SetTooltipText(self.Main).set_tooltip_text(maske_typ, feld, tooltip_text, quelle)
        return status