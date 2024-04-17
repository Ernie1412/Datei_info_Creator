import requests
from lxml import html
from urllib.parse import urlencode, urljoin
from playwright.sync_api import sync_playwright

import json
import re
from datetime import datetime
from PIL import Image
from io import BytesIO

from utils.web_scapings.datenbank_scene_maske import Infos_WebSides
from utils.database_settings.database_for_darsteller import DB_Darsteller
from gui.dialog_gender_auswahl import GenderAuswahl
from gui.dialoge_ui import StatusBar

from config import HEADERS, PROJECT_PATH, WEBINFOS_JSON_PATH

class FreeOnesInfos():

    def __init__(self, parent):
        super().__init__() 
        self.Main = parent.Main
        self.dialog = parent

    def get_FreeOne_performer_link(self):
        name=self.Main.lnEdit_performer_info.text().lower().strip()
        name1=name.replace(" ","-")
        freeone_link=f"https://www.freeones.com/{name1}/bio"
         
   
    def check_FreeOne_performer_link(self, url):
        content = None  
        if url.startswith("https://www.freeones.com/"):
            try:  
                with requests.Session() as session:
                    response = session.get(url, headers=HEADERS, timeout=12) 
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:                               
                return
            else:
                content = html.fromstring(response.content) 
        return content
    
    def open_url(self, url):
        with sync_playwright() as p:            
            page_content: str=None  
            errview: str=""         
            browser = p.chromium.launch(headless=False)
            page = browser.new_page() 
            page.set_extra_http_headers(HEADERS)
            try:                               
                page.goto(url, wait_until="domcontentloaded")                                
            except Exception as e: 
                errview = f"TimeOutError: {e}"
            else:                
                with open(str(PROJECT_PATH / 'index.html'), 'w') as f:
                    f.write(page.content())                
                page_content = html.fromstring(page.content()) 
            finally:
                browser.close()
            return errview, page_content

    
    def load_FreeOne_performer_link(self, freeone_url: str, id: int, name: str):
        type = "freeone"
        freeone_infos: dict={type:{}}         
        func_break=False
        json.dump(freeone_infos,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True)        
                        
        errview, content = self.open_url(freeone_url) 
        if errview: # per search daten suchen / default: False
            message = f"❌Fehler: {errview}"
            return            
        elif content is None:                    
            message = f"⛔ Search Link is None -> {freeone_url}"          
            return
        infos: dict={"FreeOneLink": freeone_url}     
        infos=self.sex_abfrage_iafd(freeone_url, infos)
        infos=self.namen_abfrage_iafd(content, infos)
        infos=self.rasse_abfrage_iafd(content, infos)
        infos=self.nation_abfrage_iafd(content, infos)
        infos=self.haar_abfrage_iafd(content, infos)
        infos=self.eyecolor_abfrage_iafd(content, infos)
        infos=self.gewicht_abfrage_iafd(content, infos)
        infos=self.groesse_abfrage_iafd(content, infos)
        infos=self.geburtsort_abfrage_iafd(content, infos)
        infos=self.geburtstag_abfrage_iafd(content, infos)
        infos=self.piercing_abfrage_iafd(content, infos)
        infos=self.tattoo_abfrage_iafd(content, infos)
        infos=self.aktiv_abfrage_iafd(content, infos)
        infos=self.boobs_abfrage_iafd(content, infos)
        infos=self.onlyfans_abfrage_iafd(content, infos)
        infos=self.load_image_in_label(content, id, name, infos)
        freeone_url[type]=infos
        json.dump(freeone_url,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True) 

    ### --------------------- get gender von FreeOne website mit hilfe von der URL ------------------ ### 
    def sex_abfrage_iafd(self, iafd_url, infos_webside, infos):
        _, iafd_url=iafd_url.split("/gender=",1) 
        sex_dict = {"f": 1,"m": 2}       
        sex=sex_dict.get(iafd_url[0])           
        infos["Geschlecht"]= sex    
        return infos
    ### --------------------- Ethnitiziät/Rasse und specihern in json ---------------------------- ###
    def rasse_abfrage_iafd(self, content, infos):
        datenbank_darsteller = DB_Darsteller(self.Main) 
        infos["Rassen"]= None
        rassen_ger: list=[]

        rasse_element=content.xpath("//p[contains(string(),'Ethnicity')]/following::p[1]")
        rassen_eng_text=rasse_element[0].text_content().strip() if rasse_element else None
        if rassen_eng_text not in [None, "", "No data"]:
            for rasse_eng in rassen_eng_text.split("/"):
                rasse_ger = datenbank_darsteller.get_rassen_ger_from_rassen_eng(rasse_eng)
                if rasse_ger is not None:
                    rassen_ger.append(rasse_ger)             
            infos["Rassen"] = "/".join(rassen_ger)           
        return infos
    ### ------------------- den Performer Namen von FreeOne als Alias -------------------- ###
    def namen_abfrage_iafd(self, content, infos):        
        infos["alias"]= None 

        namen_element=content.xpath("//div[@class='col-xs-12']/h1")          
        if namen_element:
            namen_text=namen_element[0].text_content().strip()   
            infos["alias"]= namen_text 
        return infos 

    def nation_abfrage_iafd(self, content, infos):        
        infos["englisch_nations"]=None 
        nations_ger=[]

        ### ---------------- von englisch(FreeOne) in deutsche(Maske) ----------------- ####
        nation_element=content.xpath("//p[contains(string(),'Nationality')]/following::p[1]")
        nations_eng=nation_element[0].text_content().strip() if nation_element else None                
        if nations_eng not in [None, "", "No data"]:
            for nation_eng in nations_eng.split(", "):
                datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)              
                nation_ger=datenbank_darsteller.get_nation_eng_to_german(str(nation_eng)) 
                nations_ger.append(nation_ger)
            infos["deutsch_nations"]=", ".join(nations_ger)        
        return infos

    ### ------------------- die Haar Farbe von FreeOne bekommen ---------------------------- ###
    def haar_abfrage_iafd(self, content, infos):        
        infos["Haarfarbe"]=None 
        
        haar_element=content.xpath("//p[contains(string(),'Hair Color')]/following::p[1]")
        haar_text=haar_element[0].text_content().strip() if haar_element else None        
        if haar_text not in [None, "", "No data"]:        
             infos["Haarfarbe"]=haar_text
        return infos

    ### ------------------- die Augen Farbe von FreeOne bekommen ---------------------------- ###
    def haar_abfrage_iafd(self, content, infos):        
        infos["Augenfarbe"]=None 
        
        eyecolor_element=content.xpath("//p[contains(string(),'Hair Color')]/following::p[1]")
        eyecolor_text=eyecolor_element[0].text_content().strip() if eyecolor_element else None        
        if eyecolor_text not in [None, "", "No data"]:        
             infos["Augenfarbe"] = eyecolor_text
        return infos

    ### ------------------- Gewicht von FreeOne bekommen ---------------------------- ###
    def gewicht_abfrage_iafd(self, content, infos):        
        infos["Gewicht"]=None 
        
        gewicht_element=content.xpath("//p[contains(string(),'Weight')]/following::p[1]")
        gewicht_text=gewicht_element[0].text_content() if gewicht_element else None        
        if gewicht_text not in [None, "", "No data"]:
            gewicht_text = re.search(r'lbs \((\d+)', gewicht_text).group(1) if re.search(r'lbs \((\d+)', gewicht_text) else ""
            infos["Gewicht"]=gewicht_text 
        return infos

    ### ------------------- Körper-Größe von FreeOne bekommen ---------------------------- ###
    def groesse_abfrage_iafd(self, content, infos):        
        infos["Groesse"]=None
        
        groesse_element=content.xpath("//p[contains(string(),'Height')]/following::p[1]")
        groesse_text=groesse_element[0].text_content().strip() if groesse_element else None        
        if groesse_text not in [None, "", "No data"]:
            groesse_text = re.search(r'inches \((\d+)', groesse_text).group(1) if re.search(r'inches \((\d+)', groesse_text) else "N/A"
            infos["Groesse"]=groesse_text
        return infos

    ### ------------------- Körper-Größe von FreeOne bekommen ---------------------------- ###
    def geburtsort_abfrage_iafd(self, content, infos):        
        infos["Birth_Place"]=None         
        geburtsort_element=content.xpath("//p[contains(string(),'Birthplace')]/following::p[1]")
        geburtsort_text=geburtsort_element[0].text_content().strip() if geburtsort_element else None        
        if geburtsort_text not in [None, "", "No data"]:
            infos["Birth_Place"] = geburtsort_text
        return infos

    def geburtstag_abfrage_iafd(self, content, infos):        
        infos["Geburtstag"]=None        
        geburtstag_element=content.xpath("//p[contains(string(),'Birthday')]/following::p[1]")
        geburtstag_text=geburtstag_element[0].text_content().strip() if geburtstag_element else None        
        if geburtstag_text not in [None, "", "No data"]:
            if " (" in geburtstag_text:
                geburtstag_text, _ = geburtstag_text.split(" (",1)
                geburtstag_text = datetime.strptime(geburtstag_text, "%B %d, %Y").strftime("%d.%m.%Y")
                infos["Geburtstag"] = geburtstag_text
        return infos

    def piercing_abfrage_iafd(self, content, infos):        
        infos["Piercing"]=None        
        piercing_element=content.xpath("//p[contains(string(),'Piercings')]/following::p[1]")
        piercing_text=piercing_element[0].text_content().strip() if piercing_element else ""
        a=self.Main.txtEdit_performer_piercing.toPlainText()      
        if piercing_text not in [None, "", "No data"]:         
             infos["Piercing"] = piercing_text 
        return infos

    def tattoo_abfrage_iafd(self, content, infos):        
        infos["Tattoo"]=None
        
        tattoo_element=content.xpath("//p[contains(string(),'Tattoos')]/following::p[1]")
        tattoo_text=tattoo_element[0].text_content().strip() if tattoo_element else ""        
        if tattoo_text not in [None, "", "No data"]:          
             infos["Tattoo"] = tattoo_text
        return infos
    
    def aktiv_abfrage_iafd(self, content, infos):
        aktiv=""        
        infos["Aktiv"]=None
        
        aktiv_element=content.xpath("//p[contains(string(),'Years Active')]/following::p[1]")
        aktiv_text=aktiv_element[0].text_content().strip() if aktiv_element else None        
        if aktiv_text not in [None, "", "No data"]: 
            if " (" in aktiv_text:
                aktiv_text,_=aktiv_text.split(" (",1)
                aktiv = "Ja" if aktiv_text.split("-",1)[1]=="2023" else "Nein"  
            aktiv_text= f"{aktiv} von: {aktiv_text}" 
            infos["Aktiv"] = aktiv_text
        return infos

    def boobs_abfrage_iafd(self, content, infos):        
        infos["Boobs"]=None 
        
        boobs_element=content.xpath("//p[contains(string(),'Measurements')]/following::p[1]")
        boobs_text=boobs_element[0].text_content().strip() if boobs_element else None        
        if boobs_text not in [None, "", "No data"]: 
            boobs_text, _ = boobs_text.split("-",1)           
            infos["Boobs"] = boobs_text  
        return infos

    def onlyfans_abfrage_iafd(self, content, infos):        
        onlyfans=[]
        infos["OnlyFans"]=None
        
        onlyfans_elements=content.xpath("//p[contains(string(),'Website')]/following::p/a[@target='starlet']")              
        if onlyfans_elements: 
            for zeile, onlyfans_text in enumerate(onlyfans_elements):
                if onlyfans_text is not None:
                    onlyfans_text=str(onlyfans_text.get('href'))
                    onlyfans.append(onlyfans_text)  
                else:
                    break            
            onlyfans="\n".join(onlyfans)
            self.Main.set_social_media_in_buttons(onlyfans)
            infos["OnlyFans"] = onlyfans        
        return infos

    def load_image_in_label(self, content, id, name, infos):        
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        image_pfad=None         
        if id.isdigit():
            artist_id=int(id)
            errview, image_pfad = datenbank_darsteller.get_biowebsite_image("IAFD", artist_id)
        if not image_pfad:
            image_url = content.xpath("//div[@id='headshot']/img")
            if image_url:
                image_url = image_url[0].get("src")
                if image_url == "https://www.iafd.com/graphics/headshots/":
                   infos["image_pfad"]=None
                   return infos
                response = requests.get(image_url, headers=HEADERS)
                image_data = response.content
                image = Image.open(BytesIO(image_data))  # webdaten in image object packen
                image_pfad = str(PROJECT_PATH / "iafd_performer.jpg")              
                image.save(image_pfad, "JPEG")                
        infos["image_pfad"]=image_pfad
        return infos


# Abschluss
if __name__ == '__main__':
    FreeOnesInfos()