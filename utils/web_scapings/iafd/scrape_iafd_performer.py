import requests
from lxml import html
from urllib.parse import urlencode, urljoin
from playwright.sync_api import sync_playwright

import json
import re
from datetime import datetime
import logging
from PIL import Image
from io import BytesIO

from utils.helpers.check_biowebsite_status import CheckBioWebsiteStatus
from gui.helpers.set_tootip_text import SetTooltipText
from utils.database_settings.database_for_darsteller import DB_Darsteller
from gui.dialog_gender_auswahl import GenderAuswahl
from gui.helpers.message_show import StatusBar

from config import HEADERS, PROJECT_PATH, WEBINFOS_JSON_PATH

class ScrapeIAFDPerformer():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow
        self.search_methode=False
        self.func_break=False
        logging.basicConfig(
            filename=PROJECT_PATH / 'ScrapeIAFDPerformer.log',
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
            self.Main.Btn_performer_in_IAFD.setToolTip(iafd_link) 
   
    def check_IAFD_performer_link(self):
        iafd_widget: str="WebSite_artist"        
        check_status=CheckBioWebsiteStatus(self.Main)
        check_status.just_checking_labelshow(iafd_widget) 
        url=self.Main.lnEdit_DBWebSite_artistLink.text()
        if url.startswith("https://www.iafd.com/person.rme/perfid="):
            try:  
                with requests.Session() as session:
                    response = session.get(url, headers=HEADERS, timeout=12) 
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                logging.error(f"check_IAFD_performer_link -> {e}")
                check_status.fehler_ausgabe_checkweb(e, iafd_widget)
                return
            else:
                content = html.fromstring(response.content)
                elements=content.xpath("//div[@class='col-xs-12']/h1")    
                if elements:
                    self.Main.lnEdit_IAFD_artistAlias.setText(elements[0].text_content().strip())
                    self.Main.performer_text_change("lnEdit_IAFD_artistAlias", color_hex='#FFFD00')                
                    check_status.check_OK_labelshow(iafd_widget)
                else:
                    if content.xpath("//div[@id='cf-error-details']"):
                        StatusBar(self.Main, "Error: 521 Fehler - Verbindung mit Cloudflare abgelehnt !")
                    check_status.check_negativ_labelshow(iafd_widget) 
        else:
            self.Main.lnEdit_create_iafd_link.setText(self.Main.lnEdit_performer_info.text()) 
            self.Main.stackedWidget.setCurrentIndex(5)
            if url:
                check_status.check_negativ_labelshow(iafd_widget)  
    
    # def block_banner(self, route):  
    #     if "revive.iafd.com/www/delivery/asyncspc.php?" in route.request.url:
    #         route.abort()     
    #     else: 
    #         route.continue_()             
    
    def handle_error(self, response, iafd_widget, check_status): 
        if response:       
            status_code = response.status  
        else:            
            message=f"⚠️TimeOutError⚠️->{self.Main.lnEdit_performer_info.text()}"
            self.Main.txtBrowser_loginfos.append(message)
            check_status.fehler_ausgabe_checkweb('TimeOutError', iafd_widget)
            return "FatalError"
        if status_code == 500:
            message=f"⚠️Error: 500 - Internal server error⚠️->{self.Main.lnEdit_performer_info.text()}"
            self.Main.txtBrowser_loginfos.append(message)
            check_status.fehler_ausgabe_checkweb('Error: 500 - Internal server error', iafd_widget)
            return "FatalError"       
        if any(keyword in response.text() for keyword in ["The page you requested was removed", "invalid or outdated page"]):
            self.search_methode=True
            status_code = "invalid"
        status_code = None if status_code==200 else status_code
        logging.error(f"open_url -> {status_code}")        
        return status_code
    
    def load_progress(self, progress):        
        self.Main.prgBar_load_status.setValue(int(progress))
    
    def open_url(self, url, iafd_widget, check_status):
        self.Main.prgBar_load_status.setValue(0)
        self.Main.stacked_image_infos.setCurrentWidget(self.Main.logger_infos)
        with sync_playwright() as p:            
            page_content: str=None  
            errview: str=""         
            browser = p.chromium.launch(headless=True)
            page = browser.new_page() 
            page.set_extra_http_headers(HEADERS) 
            #page.route("**/*", lambda route: self.block_banner(route))
            total_requests = 0
            progress = 0

            def request_started(request):
                nonlocal total_requests
                total_requests += 1

            def request_finished(request):
                nonlocal progress
                progress += 100 / total_requests
                self.load_progress(progress)                

            # Event-Handler für "request" und "requestfinished" registrieren
            page.on("request", request_started)
            page.on("requestfinished", request_finished)
            try: 
                response = page.goto(url, wait_until="domcontentloaded")
                page.query_selector("div.col-xs-12 > h1")                
            except Exception as e:                                 
                self.handle_error(e)
            else:
                errview = self.handle_error(response, iafd_widget, check_status)
                if errview not in [None, "invalid"]:
                    self.Main.prgBar_load_status.setValue(100)
                    return errview, page_content                                
                return errview, html.fromstring(page.content()) 
            finally:
                browser.close()            
    
    def load_IAFD_performer_link(self, iafd_url: str, id: int, name: str):
        tooltip_text = SetTooltipText(self.Main)
        check_status = CheckBioWebsiteStatus(self.Main)
        type = "iafd"
        iafd_infos: dict={type:{}} 
        iafd_widget: str="website_artist"
        func_break=False

        json.dump(iafd_infos,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True)        
        
        check_status.check_loading_labelshow(iafd_widget)                
        errview, content = self.open_url(iafd_url, iafd_widget, check_status)   # url aufruf mit normalen iafdlink
        if errview == 'FatalError':
            self.load_progress(100)
            return 
        if errview=="invalid" and self.search_methode:
            self.load_progress(10) # per search daten suchen / default: False
            message="⚠️nichts direktes gefunden. ℹ️ Wende Such-Methode an: "
            self.Main.txtBrowser_loginfos.append(message)
            iafd_url=self.generate_iafd_search_url(self.Main.lnEdit_performer_info.text()) # url aufruf mit search iafdlink               
            errview, content = self.open_url(iafd_url, iafd_widget, check_status) 
            if errview == 'FatalError':
                self.load_progress(100)
                return  
            if content is None:                    
                self.Main.Btn_performer_in_IAFD.setToolTip("")
                self.Main.lnEdit_DBWebSite_artistLink.setText("") 
                logging.warning(f"⛔ Search Link is None -> {iafd_url}")
                last_line = self.Main.txtBrowser_loginfos.toPlainText().split('\n')[-1]                
                message=f"{last_line}❌ Such Methode erfolglos: {self.Main.lnEdit_performer_info.text()}" 
                self.Main.txtBrowser_loginfos.setText(self.Main.txtBrowser_loginfos.toPlainText().rstrip(last_line) + message)  
                self.load_progress(100)                
                return 
            gender_auswahl=GenderAuswahl(self.Main, False)             
            if  gender_auswahl.get_gender_for_iafdlink() == "f":
                actors_list=content.xpath("//table[@id='tblFem']/tbody/tr[@class='odd']/td[1]/a") # weiblich
            else:
                actors_list=content.xpath("//table[@id='tblMal']/tbody/tr[@class='odd']/td[1]/a") # männlich
            if len(actors_list)== 1:
                self.search_methode=False
                iafd_url = urljoin("https://www.iafd.com", actors_list[0].get('href'))
                errview, content = self.open_url(iafd_url, iafd_widget, check_status)
                if errview == 'FatalError':
                    self.load_progress(100)
                    return
                self.Main.Btn_performer_in_IAFD.setToolTip(iafd_url)
                self.Main.lnEdit_DBWebSite_artistLink.setText(iafd_url)  
                last_line = self.Main.txtBrowser_loginfos.toPlainText().split('\n')[-1]
                message=f"{last_line}✅ Such Methode erfolgreich: {self.Main.lnEdit_performer_info.text()}"
                self.Main.txtBrowser_loginfos.setText(self.Main.txtBrowser_loginfos.toPlainText().rstrip(last_line) + message)                  
            else:
                check_status.check_negativ_labelshow(iafd_widget)
                logging.warning(f"❌ Mehr als 1 Performer > {len(actors_list)} -> {iafd_url}") 
                last_line = self.Main.txtBrowser_loginfos.toPlainText().split('\n')[-1]
                message=f"❌ Mehr als 1 Performer > {len(actors_list)}"
                self.Main.txtBrowser_loginfos.setText(self.Main.txtBrowser_loginfos.toPlainText().rstrip(last_line) + message)
                self.Main.Btn_performer_in_IAFD.setToolTip("")
                self.Main.lnEdit_DBWebSite_artistLink.setText("") 
                self.load_progress(100)
                return
        self.load_progress(70)
        infos: dict={"IAFDLink": iafd_url}     
        infos=self.sex_abfrage_iafd(iafd_url, infos, value=71)
        infos=self.namen_abfrage_iafd(content, infos, value=72)
        infos=self.rasse_abfrage_iafd(content, tooltip_text, infos, value=73)
        infos=self.nation_abfrage_iafd(content, infos, value=74)
        infos=self.haar_abfrage_iafd(content, tooltip_text, infos, value=75)
        infos=self.gewicht_abfrage_iafd(content, tooltip_text, infos, value=76)
        infos=self.groesse_abfrage_iafd(content, tooltip_text, infos, value=77)
        infos=self.geburtsort_abfrage_iafd(content, tooltip_text, infos, value=78)
        infos=self.geburtstag_abfrage_iafd(content, tooltip_text, infos, value=79)
        infos=self.piercing_abfrage_iafd(content, tooltip_text, infos, value=80)
        infos=self.tattoo_abfrage_iafd(content, tooltip_text, infos, value=81)
        infos=self.aktiv_abfrage_iafd(content, tooltip_text, infos, value=82)
        infos=self.boobs_abfrage_iafd(content, tooltip_text, infos, value=83)
        infos=self.onlyfans_abfrage_iafd(content, infos, value=84)
        infos=self.load_image_in_label(content, id, name, infos, value=99)
        iafd_infos[type]=infos
        json.dump(iafd_infos,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True)
        check_status.check_loaded_labelshow("website_artist") 
        self.load_progress(100)             
      
    def generate_iafd_search_url(self, search_term):
        base_url = "https://www.iafd.com/ramesearch.asp"
        params = {
            "searchtype": "comprehensive",
            "searchstring": search_term.replace(" ", "+")  }        
        return f"{base_url}?{urlencode(params, safe='+')}" # search_url von iafd
    
    ### --------------------- get gender von IAFD website mit hilfe von der URL ------------------ ### 
    def sex_abfrage_iafd(self, iafd_url, infos, value):
        _, iafd_url=iafd_url.split("/gender=",1) 
        sex_dict = {"f": 1,"m": 2}       
        sex=sex_dict.get(iafd_url[0])           
        infos["Geschlecht"]= sex 
        self.load_progress(value)   
        return infos
    ### --------------------- Ethnitiziät/Rasse und specihern in json ---------------------------- ###
    def rasse_abfrage_iafd(self, content, tooltip_text, infos, value):
        datenbank_darsteller = DB_Darsteller(self.Main) 
        infos["Rassen"]= None
        rassen_ger: list=[]

        rasse_element=content.xpath("//p[contains(string(),'Ethnicity')]/following::p[1]")
        rassen_eng_text=rasse_element[0].text_content().strip() if rasse_element else None
        if rassen_eng_text not in ['None', 'No data', None]:
            for rasse_eng in rassen_eng_text.split("/"):
                rasse_ger = datenbank_darsteller.get_rassen_ger_from_rassen_eng(rasse_eng)
                if rasse_ger == None:
                    logging.error(f"⛔ Rasse nicht gefunden: {rasse_eng}")
                else:
                    rassen_ger.append(rasse_ger)             
            infos["Rassen"] = "/".join(rassen_ger)           
        tooltip_text.set_tooltip_text("cBox_performer_", "rasse", f"IAFD: {rassen_eng_text}", "IAFD")  
        self.load_progress(value)      
        return infos
    ### ------------------- den Performer Namen von IAFD als Alias -------------------- ###
    def namen_abfrage_iafd(self, content, infos, value):        
        infos["alias"]= None 

        namen_element=content.xpath("//div[@class='col-xs-12']/h1")          
        if namen_element:
            namen_text=namen_element[0].text_content().strip()   
            infos["alias"]= namen_text 
        self.load_progress(value)
        return infos 

    def nation_abfrage_iafd(self, content, infos, value):        
        infos["englisch_nations"]=None 
        nations_ger=[]

        ### ---------------- von englisch(IAFD) in deutsche(Maske) ----------------- ####
        nation_element=content.xpath("//p[contains(string(),'Nationality')]/following::p[1]")
        nations_eng=nation_element[0].text_content().strip() if nation_element else None                
        if nations_eng not in ['None', 'No data', None]:
            for nation_eng in nations_eng.split(", "):
                datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)              
                nation_ger = datenbank_darsteller.get_nation_eng_to_german(str(nation_eng))
                if nation_ger is not None:                    
                    nations_ger.append(nation_ger)            
            if nations_ger:
                infos["deutsch_nations"]=", ".join(nations_ger)   
        self.load_progress(value)      
        return infos

    ### ------------------- die Haar Farbe von IAFD bekommen ---------------------------- ###
    def haar_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Haarfarbe"]=None 
        
        haar_element=content.xpath("//p[contains(string(),'Hair Color')]/following::p[1]")
        haar_text=haar_element[0].text_content().strip() if haar_element else None        
        if haar_text not in ['None', 'No data', None]:        
             infos["Haarfarbe"]=haar_text
        tooltip_text.set_tooltip_text("lnEdit_performer_", "hair", f"IAFD: {haar_text}", "IAFD")
        self.load_progress(value) 
        return infos

    ### ------------------- Gewicht von IAFD bekommen ---------------------------- ###
    def gewicht_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Gewicht"]=None 
        
        gewicht_element=content.xpath("//p[contains(string(),'Weight')]/following::p[1]")
        gewicht_text=gewicht_element[0].text_content() if gewicht_element else None        
        if gewicht_text not in ['None', 'No data', None]:
            gewicht_text = re.search(r'lbs \((\d+)', gewicht_text).group(1) if re.search(r'lbs \((\d+)', gewicht_text) else ""
            infos["Gewicht"]=gewicht_text 
        tooltip_text.set_tooltip_text("lnEdit_performer_", "weight", f"IAFD: {gewicht_text} kg", "IAFD")
        self.load_progress(value) 
        return infos

    ### ------------------- Körper-Größe von IAFD bekommen ---------------------------- ###
    def groesse_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Groesse"]=None
        
        groesse_element=content.xpath("//p[contains(string(),'Height')]/following::p[1]")
        groesse_text=groesse_element[0].text_content().strip() if groesse_element else None        
        if groesse_text not in ['None', 'No data', None]:
            groesse_text = re.search(r'inches \((\d+)', groesse_text).group(1) if re.search(r'inches \((\d+)', groesse_text) else "N/A"
            infos["Groesse"]=groesse_text
        tooltip_text.set_tooltip_text("lnEdit_performer_", "height", f"IAFD: {groesse_text} cm", "IAFD")
        self.load_progress(value) 
        return infos

    ### ------------------- Körper-Größe von IAFD bekommen ---------------------------- ###
    def geburtsort_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Birth_Place"]=None         
        geburtsort_element=content.xpath("//p[contains(string(),'Birthplace')]/following::p[1]")
        geburtsort_text=geburtsort_element[0].text_content().strip() if geburtsort_element else None        
        if geburtsort_text not in ['None', 'No data', None]:
            infos["Birth_Place"] = geburtsort_text
        tooltip_text.set_tooltip_text("lnEdit_performer_", "birthplace", f"IAFD: {geburtsort_text}", "IAFD")
        self.load_progress(value) 
        return infos

    def geburtstag_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Geburtstag"]=None        
        geburtstag_element=content.xpath("//p[contains(string(),'Birthday')]/following::p[1]")
        geburtstag_text=geburtstag_element[0].text_content().strip() if geburtstag_element else None        
        if geburtstag_text not in ['None', 'No data', None]:
            if " (" in geburtstag_text:
                geburtstag_text, _ = geburtstag_text.split(" (",1)
                geburtstag_text = datetime.strptime(geburtstag_text, "%B %d, %Y").strftime("%d.%m.%Y")
                infos["Geburtstag"] = geburtstag_text
        tooltip_text.set_tooltip_text("lnEdit_performer_", "birthday", f"IAFD: {geburtstag_text}", "IAFD")
        self.load_progress(value) 
        return infos

    def piercing_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Piercing"]=None        
        piercing_element=content.xpath("//p[contains(string(),'Piercings')]/following::p[1]")
        piercing_text=piercing_element[0].text_content().strip() if piercing_element else ""
        a=self.Main.txtEdit_performer_piercing.toPlainText()      
        if piercing_text not in ['No data', 'None', None]:         
             infos["Piercing"] = piercing_text 
        tooltip_text.set_tooltip_text("txtEdit_performer_", "piercing", f"IAFD: {piercing_text[:40]}", "IAFD")
        self.load_progress(value) 
        return infos

    def tattoo_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Tattoo"] = None
        
        tattoo_element=content.xpath("//p[contains(string(),'Tattoos')]/following::p[1]")
        tattoo_text = tattoo_element[0].text_content().strip() if tattoo_element else ""        
        if tattoo_text not in ['No data', 'None', None]:          
             infos["Tattoo"] = tattoo_text
        tooltip_text.set_tooltip_text("txtEdit_performer_", "tattoo", f"IAFD: {tattoo_text[:40]}", "IAFD")
        self.load_progress(value) 
        return infos
    
    def aktiv_abfrage_iafd(self, content, tooltip_text, infos, value):
        aktiv=""        
        infos["Aktiv"]=None
        
        aktiv_element=content.xpath("//p[contains(string(),'Years Active')]/following::p[1]")
        aktiv_text=aktiv_element[0].text_content().strip() if aktiv_element else None        
        if aktiv_text not in ['None', 'No data', None]: 
            if " (" in aktiv_text:
                aktiv_text,_=aktiv_text.split(" (",1)
                aktiv = "Ja" if aktiv_text.split("-",1)[1]=="2023" else "Nein"  
            aktiv_text= f"{aktiv} von: {aktiv_text}" 
            infos["Aktiv"] = aktiv_text
        tooltip_text.set_tooltip_text("lnEdit_performer_", "activ", f"IAFD: {aktiv_text}", "IAFD")
        self.load_progress(value) 
        return infos

    def boobs_abfrage_iafd(self, content, tooltip_text, infos, value):        
        infos["Boobs"]=None 
        
        boobs_element=content.xpath("//p[contains(string(),'Measurements')]/following::p[1]")
        boobs_text = boobs_element[0].text_content().strip() if boobs_element else None        
        if boobs_text not in ['None', 'No data', None]: 
            boobs_text, _ = boobs_text.split("-",1)           
            infos["Boobs"] = boobs_text  
        tooltip_text.set_tooltip_text("lnEdit_performer_", "boobs", f"IAFD: {boobs_text}", "IAFD")
        self.load_progress(value) 
        return infos

    def onlyfans_abfrage_iafd(self, content, infos, value):        
        onlyfans=[]
        infos["OnlyFans"]=None
        
        onlyfans_elements=content.xpath("//p[contains(string(),'Website')]/following::p/a[@target='starlet']")              
        if onlyfans_elements: 
            for zeile, onlyfans_text in enumerate(onlyfans_elements):
                if len(onlyfans_text):
                    onlyfans_text=str(onlyfans_text.get('href'))
                    onlyfans.append(onlyfans_text)  
                else:
                    break            
            onlyfans="\n".join(onlyfans)
            self.Main.set_social_media_in_buttons(onlyfans)
            infos["OnlyFans"] = onlyfans  
        self.load_progress(value)       
        return infos

    def load_image_in_label(self, content, id, name, infos, value):        
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        image_pfad=None 
        image_url: str=""        
        if id.isdigit():
            artist_id=int(id)
            image_pfad = datenbank_darsteller.get_biowebsite_image("IAFD", artist_id)
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
        infos["image_pfad"] = image_pfad
        infos["image_url"] = image_url
        self.load_progress(value) 
        return infos


# Abschluss
if __name__ == '__main__':
    ScrapeIAFDPerformer()