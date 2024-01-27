from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QCoreApplication

import requests
from lxml import html
from urllib.parse import urlencode, urljoin
from playwright.sync_api import sync_playwright

import json
import re
from datetime import datetime
import logging
import time
from PIL import Image
from io import BytesIO

from utils.web_scapings.websides import Infos_WebSides
from utils.database_settings.database_for_darsteller import DB_Darsteller
from gui.dialog_gender_auswahl import GenderAuswahl
from gui.dialoge_ui import StatusBar

from config import HEADERS, PROJECT_PATH, WEBINFOS_JSON_PATH

class IAFDInfos():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow
        self.search_methode=False
        self.func_break=False
        logging.basicConfig(
            filename=PROJECT_PATH / 'IAFDInfos.log',
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S' )

    def get_IAFD_performer_link(self):
        name=self.Main.lnEdit_create_iafd_link.text().lower().strip()
        gender=GenderAuswahl(self.Main, False).get_gender_for_iafdlink()
        if gender:            
            name1=name.replace(" ","")
            name2=name.replace(" ","-")
            iafd_link=f"https://www.iafd.com/person.rme/perfid={name1}/gender={gender}/{name2}.htm"
            self.Main.lnEdit_DBIAFD_artistLink.setText(iafd_link) 
   
    def check_IAFD_performer_link(self):
        iafd_widget: str="IAFD_artist"        
        infos_webside=Infos_WebSides(self.Main)
        infos_webside.just_checking_labelshow(iafd_widget) 
        url=self.Main.lnEdit_DBIAFD_artistLink.text()
        if url.startswith("https://www.iafd.com/person.rme/perfid="):
            try:  
                with requests.Session() as session:
                    response = session.get(url, headers=HEADERS, timeout=12) 
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                logging.error(f"check_IAFD_performer_link -> {e}")
                infos_webside.fehler_ausgabe_checkweb(e, iafd_widget)
                return
            else:
                content = html.fromstring(response.content)
                elements=content.xpath("//div[@class='col-xs-12']/h1")    
                if elements:
                    self.Main.lnEdit_IAFD_artistAlias.setText(elements[0].text_content().strip())
                    self.Main.performer_text_change("lnEdit_IAFD_artistAlias", color_hex='#FFFD00')                
                    infos_webside.check_OK_labelshow(iafd_widget)
                else:
                    if content.xpath("//div[@id='cf-error-details']"):
                        StatusBar(self.Main, "Error: 521 Fehler - Verbindung mit Cloudflare abgelehnt !")
                    infos_webside.check_negativ_labelshow(iafd_widget) 
        else:
            self.Main.lnEdit_create_iafd_link.setText(self.Main.lnEdit_performer_info.text()) 
            self.Main.stackedWidget.setCurrentIndex(5)
            if url:
                infos_webside.check_negativ_labelshow(iafd_widget)    

    def check_fatal_errors(self, errview: str, iafd_widget, infos_webside):
        if "TimeOutError" in errview:
            message=f"⚠️{errview}⚠️->{self.Main.lnEdit_performer_info.text()}"
            self.Main.txtBrowser_loginfos.append(message)
            infos_webside.fehler_ausgabe_checkweb(errview, iafd_widget) 
            return True           
        elif "500" in errview: 
            message=f"⚠️{errview}⚠️->{self.Main.lnEdit_performer_info.text()}"
            self.Main.txtBrowser_loginfos.append(message)
            infos_webside.fehler_ausgabe_checkweb(errview, iafd_widget)            
            return True        
    
    def block_banner(self, route):  
        if "revive.iafd.com/www/delivery/asyncspc.php?" in route.request.url:            
            route.abort()
        else:
            route.continue_()

    def open_url(self, url, iafd_widget):
        with sync_playwright() as p:            
            page_content: str=None  
            errview: str=""         
            browser = p.chromium.launch(headless=False)
            page = browser.new_page() 
            page.set_extra_http_headers(HEADERS) 
            page.route("**/*", lambda route: self.block_banner(route))
            try:                               
                page.goto(url, wait_until="domcontentloaded")
                page.query_selector("div.col-xs-12 > h1")                
            except Exception as e:                                 
                logging.error(f"open_url -> {e}")                 
                errview = f"TimeOutError: {e}"
            else:
                if any(keyword in page.content() for keyword in ["500 - Internal server error"]):
                    return "Error: 500 - Internal server error", page_content
                if any(keyword in page.content() for keyword in ["The page you requested was removed", "invalid or outdated page"]):
                    self.search_methode=True
                    return "invalid", None
                with open(str(PROJECT_PATH / 'index.html'), 'w') as f:
                    f.write(page.content())
                # div1_content = page.query_selector("div.col-xs-12.col-sm-3")
                # div2_content = page.query_selector("div.col-xs-12 > h1")
                # div3_contents = page.query_selector("div.col-xs-12.col-sm-4")
                page_content = html.fromstring(page.content()) 
            finally:
                browser.close()
            return errview, page_content

    
    def load_IAFD_performer_link(self, iafd_url: str, id: int, name: str):
        type = "iafd"
        iafd_infos: dict={type:{}} 
        iafd_widget: str="IAFD_artist"
        func_break=False

        json.dump(iafd_infos,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True)
        
        infos_webside=Infos_WebSides(self.Main)
        infos_webside.check_loading_labelshow(iafd_widget)                
        errview, content = self.open_url(iafd_url, iafd_widget)   # url aufruf mit normalen iafdlink
        func_break=self.check_fatal_errors(errview, iafd_widget, infos_webside)
        if func_break:
            return
        if errview=="invalid" and self.search_methode: # per search daten suchen / default: False
            message="⚠️nichts direktes gefunden. ℹ️ Wende Such-Methode an: "
            self.Main.txtBrowser_loginfos.append(message)
            iafd_url=self.generate_iafd_search_url(self.Main.lnEdit_performer_info.text()) # url aufruf mit search iafdlink               
            errview, content = self.open_url(iafd_url, iafd_widget) 
            func_break = self.check_fatal_errors(errview, iafd_widget, infos_webside) 
            if func_break:
                return
            if content is None:                    
                self.Main.lnEdit_DBIAFD_artistLink.setText("") 
                logging.warning(f"⛔ Search Link is None -> {iafd_url}")
                last_line = self.Main.txtBrowser_loginfos.toPlainText().split('\n')[-1]                
                message=f"{last_line}❌ Such Methode erfolglos: {self.Main.lnEdit_performer_info.text()}" 
                self.Main.txtBrowser_loginfos.setText(self.Main.txtBrowser_loginfos.toPlainText().rstrip(last_line) + message)                  
                return 
            gender_auswahl=GenderAuswahl(self.Main, False)             
            if  gender_auswahl.get_gender_for_iafdlink() == "f":
                actors_list=content.xpath("//table[@id='tblFem']/tbody/tr[@class='odd']/td[1]/a") # weiblich
            else:
                actors_list=content.xpath("//table[@id='tblMal']/tbody/tr[@class='odd']/td[1]/a") # männlich
            if len(actors_list)== 1:
                self.search_methode=False
                iafd_url = urljoin("https://www.iafd.com", actors_list[0].get('href'))
                errview, content = self.open_url(iafd_url, iafd_widget)
                func_break = self.check_fatal_errors(errview, iafd_widget, infos_webside)
                if func_break:
                    return
                self.Main.lnEdit_DBIAFD_artistLink.setText(iafd_url) 
                last_line = self.Main.txtBrowser_loginfos.toPlainText().split('\n')[-1]
                message=f"{last_line}✅ Such Methode erfolgreich: {self.Main.lnEdit_performer_info.text()}"
                self.Main.txtBrowser_loginfos.setText(self.Main.txtBrowser_loginfos.toPlainText().rstrip(last_line) + message)                  
            else:
                infos_webside.check_negativ_labelshow(iafd_widget)
                logging.warning(f"❌ Mehr als 1 Performer > {len(actors_list)} -> {iafd_url}") 
                last_line = self.Main.txtBrowser_loginfos.toPlainText().split('\n')[-1]
                message=f"❌ Mehr als 1 Performer > {len(actors_list)}"
                self.Main.txtBrowser_loginfos.setText(self.Main.txtBrowser_loginfos.toPlainText().rstrip(last_line) + message)
                self.Main.lnEdit_DBIAFD_artistLink.setText("")
                return
        infos: dict={"IAFDLink": iafd_url}     
        infos=self.sex_abfrage_iafd(iafd_url, infos_webside, infos)
        infos=self.namen_abfrage_iafd(content, infos_webside, infos)
        infos=self.rasse_abfrage_iafd(content, infos_webside, infos)
        infos=self.nation_abfrage_iafd(content, infos_webside, infos)
        infos=self.haar_abfrage_iafd(content, infos_webside, infos)
        infos=self.gewicht_abfrage_iafd(content, infos_webside, infos)
        infos=self.groesse_abfrage_iafd(content, infos_webside, infos)
        infos=self.geburtsort_abfrage_iafd(content, infos_webside, infos)
        infos=self.geburtstag_abfrage_iafd(content, infos_webside, infos)
        infos=self.piercing_abfrage_iafd(content, infos_webside, infos)
        infos=self.tattoo_abfrage_iafd(content, infos_webside, infos)
        infos=self.aktiv_abfrage_iafd(content, infos_webside, infos)
        infos=self.boobs_abfrage_iafd(content, infos_webside, infos)
        infos=self.onlyfans_abfrage_iafd(content, infos_webside, infos)
        infos=self.load_image_in_label(content, id, name, infos)
        iafd_infos[type]=infos
        json.dump(iafd_infos,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True)
        infos_webside.check_loaded_labelshow("IAFD_artist")              
      
    def generate_iafd_search_url(self, search_term):
        base_url = "https://www.iafd.com/ramesearch.asp"
        params = {
            "searchtype": "comprehensive",
            "searchstring": search_term.replace(" ", "+")  }        
        return f"{base_url}?{urlencode(params, safe='+')}" # search_url von iafd
    
    ### --------------------- get gender von IAFD website mit hilfe von der URL ------------------ ### 
    def sex_abfrage_iafd(self, iafd_url, infos_webside, infos):
        _, iafd_url=iafd_url.split("/gender=",1) 
        sex_dict = {"f": 1,"m": 2}       
        sex=sex_dict.get(iafd_url[0])           
        infos["Geschlecht"]= sex    
        return infos
    ### --------------------- Ethnitiziät/Rasse und specihern in json ---------------------------- ###
    def rasse_abfrage_iafd(self, content, infos_webside, infos):
        datenbank_darsteller = DB_Darsteller(self.Main) 
        infos["Rassen"]= None
        rassen_ger: list=[]

        rasse_element=content.xpath("//p[contains(string(),'Ethnicity')]/following::p[1]")
        rassen_eng_text=rasse_element[0].text_content().strip() if rasse_element else None
        if rassen_eng_text not in [None, "", "No data"]:
            for rasse_eng in rassen_eng_text.split("/"):
                rasse_ger = datenbank_darsteller.get_rassen_ger_from_rassen_eng(rasse_eng)
                if rasse_ger == None:
                    logging.error(f"⛔ Rasse nicht gefunden: {rasse_eng}")
                else:
                    rassen_ger.append(rasse_ger)             
            infos["Rassen"] = "/".join(rassen_ger)           
        infos_webside.set_tooltip_text("cBox_performer_", "rasse", f"IAFD: {rassen_eng_text}", "IAFD")        
        return infos
    ### ------------------- den Performer Namen von IAFD als Alias -------------------- ###
    def namen_abfrage_iafd(self, content, infos_webside, infos):        
        infos["alias"]= None 

        namen_element=content.xpath("//div[@class='col-xs-12']/h1")          
        if namen_element:
            namen_text=namen_element[0].text_content().strip()   
            infos["alias"]= namen_text 
        return infos 

    def nation_abfrage_iafd(self, content, infos_webside, infos):        
        infos["englisch_nations"]=None 
        nations_ger=[]

        ### ---------------- von englisch(IAFD) in deutsche(Maske) ----------------- ####
        nation_element=content.xpath("//p[contains(string(),'Nationality')]/following::p[1]")
        nations_eng=nation_element[0].text_content().strip() if nation_element else None                
        if nations_eng not in [None, "", "No data"]:
            for nation_eng in nations_eng.split(", "):
                datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)              
                nation_ger=datenbank_darsteller.get_nation_eng_to_german(str(nation_eng)) 
                nations_ger.append(nation_ger)
            infos["deutsch_nations"]=", ".join(nations_ger)        
        return infos

    ### ------------------- die Haar Farbe von IAFD bekommen ---------------------------- ###
    def haar_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Haarfarbe"]=None 
        
        haar_element=content.xpath("//p[contains(string(),'Hair Color')]/following::p[1]")
        haar_text=haar_element[0].text_content().strip() if haar_element else None        
        if haar_text not in [None, "", "No data"]:        
             infos["Haarfarbe"]=haar_text
        infos_webside.set_tooltip_text("lnEdit_performer_", "hair", f"IAFD: {haar_text}", "IAFD")
        return infos

    ### ------------------- Gewicht von IAFD bekommen ---------------------------- ###
    def gewicht_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Gewicht"]=None 
        
        gewicht_element=content.xpath("//p[contains(string(),'Weight')]/following::p[1]")
        gewicht_text=gewicht_element[0].text_content() if gewicht_element else None        
        if gewicht_text not in [None, "", "No data"]:
            gewicht_text = re.search(r'lbs \((\d+)', gewicht_text).group(1) if re.search(r'lbs \((\d+)', gewicht_text) else ""
            infos["Gewicht"]=gewicht_text 
        infos_webside.set_tooltip_text("lnEdit_performer_", "weight", f"IAFD: {gewicht_text} kg", "IAFD")
        return infos

    ### ------------------- Körper-Größe von IAFD bekommen ---------------------------- ###
    def groesse_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Groesse"]=None
        
        groesse_element=content.xpath("//p[contains(string(),'Height')]/following::p[1]")
        groesse_text=groesse_element[0].text_content().strip() if groesse_element else None        
        if groesse_text not in [None, "", "No data"]:
            groesse_text = re.search(r'inches \((\d+)', groesse_text).group(1) if re.search(r'inches \((\d+)', groesse_text) else "N/A"
            infos["Groesse"]=groesse_text
        infos_webside.set_tooltip_text("lnEdit_performer_", "height", f"IAFD: {groesse_text} cm", "IAFD")
        return infos

    ### ------------------- Körper-Größe von IAFD bekommen ---------------------------- ###
    def geburtsort_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Birth_Place"]=None 
        
        geburtsort_element=content.xpath("//p[contains(string(),'Birthplace')]/following::p[1]")
        geburtsort_text=geburtsort_element[0].text_content().strip() if geburtsort_element else None        
        if geburtsort_text not in [None, "", "No data"]:
            infos["Birth_Place"] = geburtsort_text
        infos_webside.set_tooltip_text("lnEdit_performer_", "birthplace", f"IAFD: {geburtsort_text}", "IAFD")
        return infos

    def geburtstag_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Geburtstag"]=None
        
        geburtstag_element=content.xpath("//p[contains(string(),'Birthday')]/following::p[1]")
        geburtstag_text=geburtstag_element[0].text_content().strip() if geburtstag_element else None        
        if geburtstag_text not in [None, "", "No data"]:
            if " (" in geburtstag_text:
                geburtstag_text, _ = geburtstag_text.split(" (",1)
                geburtstag_text = datetime.strptime(geburtstag_text, "%B %d, %Y").strftime("%d.%m.%Y")
                infos["Geburtstag"] = geburtstag_text
        infos_webside.set_tooltip_text("lnEdit_performer_", "birthday", f"IAFD: {geburtstag_text}", "IAFD")
        return infos

    def piercing_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Piercing"]=None 
        
        piercing_element=content.xpath("//p[contains(string(),'Piercings')]/following::p[1]")
        piercing_text=piercing_element[0].text_content().strip() if piercing_element else ""
        a=self.Main.txtEdit_performer_piercing.toPlainText()      
        if piercing_text not in [None, "", "No data"]:         
             infos["Piercing"] = piercing_text 
        infos_webside.set_tooltip_text("txtEdit_performer_", "piercing", f"IAFD: {piercing_text[:40]}", "IAFD")
        return infos

    def tattoo_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Tattoo"]=None
        
        tattoo_element=content.xpath("//p[contains(string(),'Tattoos')]/following::p[1]")
        tattoo_text=tattoo_element[0].text_content().strip() if tattoo_element else ""        
        if tattoo_text not in [None, "", "No data"]:          
             infos["Tattoo"] = tattoo_text
        infos_webside.set_tooltip_text("txtEdit_performer_", "tattoo", f"IAFD: {tattoo_text[:40]}", "IAFD")
        return infos
    
    def aktiv_abfrage_iafd(self, content, infos_webside, infos):
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
        infos_webside.set_tooltip_text("lnEdit_performer_", "activ", f"IAFD: {aktiv_text}", "IAFD")
        return infos

    def boobs_abfrage_iafd(self, content, infos_webside, infos):        
        infos["Boobs"]=None 
        
        boobs_element=content.xpath("//p[contains(string(),'Measurements')]/following::p[1]")
        boobs_text=boobs_element[0].text_content().strip() if boobs_element else None        
        if boobs_text not in [None, "", "No data"]: 
            boobs_text, _ = boobs_text.split("-",1)           
            infos["Boobs"] = boobs_text  
        infos_webside.set_tooltip_text("lnEdit_performer_", "boobs", f"IAFD: {boobs_text}", "IAFD")
        return infos

    def onlyfans_abfrage_iafd(self, content, infos_webside, infos):        
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
            errview, image_pfad = datenbank_darsteller.get_iafd_image(artist_id, name)
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
    IAFDInfos()