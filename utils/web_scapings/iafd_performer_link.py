from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import requests
from lxml import html

import pyperclip
import json
import re
from datetime import datetime

from utils.web_scapings.websides import Infos_WebSides
from utils.database_settings.database_for_darsteller import DB_Darsteller

from config import HEADERS, PROJECT_PATH, RASSE_JSON

class IAFDInfos():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow

    def get_IAFD_performer_link(self):
        name=self.Main.lnEdit_IAFD_performer.text().lower().strip()
        cbox_sex=self.Main.cBox_performer_sex.currentText()
        sex = self.dict_sex(cbox_sex,cbox=True) 
        if sex:            
            name1=name.replace(" ","")
            name2=name.replace(" ","-")
            iafd_link=f"https://www.iafd.com/person.rme/perfid={name1}/gender={sex}/{name2}.htm"
            self.Main.lnEdit_DBIAFD_artistLink.setText(iafd_link)            
            pyperclip.copy(iafd_link)
   
    def check_IAFD_performer_link(self):
        webdatabase: str="IAFD_artist"
        
        infos_webside=Infos_WebSides(self.Main)

        infos_webside.just_checking_labelshow(webdatabase) 
        if self.Main.lnEdit_DBIAFD_artistLink.text().startswith("https://www.iafd.com/person.rme/perfid="):
            try:                    
                r = requests.get(self.Main.lnEdit_DBIAFD_artistLink.text(), headers=HEADERS, timeout=10)
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                infos_webside.fehler_ausgabe_checkweb(e,"IAFD_artistURL")
                return
            else:               
                if html.fromstring(r.content).xpath('//div[@class="col-xs-12"]/h1'):                
                    infos_webside.check_OK_labelshow(webdatabase)
                else:
                    infos_webside.check_negativ_labelshow(webdatabase)  
        else:
            self.Main.lnEdit_IAFD_performer.setText(self.Main.lnEdit_performer_info.text())  
            self.Main.lnEdit_IAFD_performer.setFocus()          
            self.Main.stackedWidget.setCurrentIndex(5)
            infos_webside.check_error_labelshow(webdatabase)
    
    def dict_sex(self,cbox_sex,cbox=None):
        sex_dict={"weiblich": "f", "männlich": "m"}
        if cbox==True:
            sex=sex_dict.get(cbox_sex)
        else:
            sex_dict={"f":"weiblich", "m": "männlich"}
            sex=sex_dict.get(cbox_sex)
        return sex
    
    def load_IAFD_performer_link(self):
        webdatabase: str="IAFD_artist"
        infos_webside=Infos_WebSides(self.Main)
        infos_webside.check_loading_labelshow(webdatabase)
        url = self.Main.lnEdit_DBIAFD_artistLink.text()        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            infos_webside.fehler_ausgabe_checkweb(e,f"{webdatabase}URL")
            status = e           
        else:
            content = html.fromstring(response.content)               
            if not content.xpath('//div[@class="col-xs-12"]/h1'): 
                infos_webside.check_negativ_labelshow(webdatabase) 
                return 

            self.sex_abfrage_iafd(url, infos_webside)
            self.rasse_abfrage_iafd(content, infos_webside)
            self.nation_abfrage_iafd(content, infos_webside)
            self.haar_abfrage_iafd(content, infos_webside)
            self.gewicht_abfrage_iafd(content, infos_webside)
            self.groesse_abfrage_iafd(content, infos_webside)
            self.geburtsort_abfrage_iafd(content, infos_webside)
            self.geburtstag_abfrage_iafd(content, infos_webside)
            self.piercing_abfrage_iafd(content, infos_webside)
            self.tattoo_abfrage_iafd(content, infos_webside)
            self.aktiv_abfrage_iafd(content, infos_webside)
            self.boobs_abfrage_iafd(content, infos_webside)
            self.onlyfans_abfrage_iafd(content, infos_webside)
            self.load_image_in_label(content)
            infos_webside.check_loaded_labelshow("IAFD_artist")
    
    def sex_abfrage_iafd(self, url, infos_webside):
        _, url=url.split("/gender=",1)        
        sex=self.dict_sex(url[0])  
        index=self.Main.cBox_performer_sex.findText(sex)        
        self.Main.cBox_performer_sex.setCurrentIndex(index)        
        infos_webside.set_tooltip_text("cBox_performer_", "sex", f"IAFD: {sex}", "IAFD")
    
    def rasse_abfrage_iafd(self, content, infos_webside):        
        rasse_text=None 
        
        rasse_element=content.xpath("//p[contains(string(),'Ethnicity')]/following::p[1]")
        rasse_text=rasse_element[0].text_content() if rasse_element else None        
        rasse_dict= json.loads(RASSE_JSON.read_bytes())
        if rasse_text not in (None, "", "No data"):        
            index=self.Main.cBox_performer_rasse.findText(rasse_dict["eng_ger"].get(rasse_text,""))            
            self.Main.cBox_performer_rasse.setCurrentIndex(index)            
        infos_webside.set_tooltip_text("cBox_performer_", "rasse", f"IAFD: {rasse_text}", "IAFD")

    def nation_abfrage_iafd(self, content, infos_webside):        
        nation_text=None 
        ### ---------------- von englisch(IAFD) in deutsche(Maske) ----------------- ####
        nation_element=content.xpath("//p[contains(string(),'Nationality')]/following::p[1]")
        nations_eng=nation_element[0].text_content() if nation_element else None                
        if nations_eng not in (None, "", "No data"):
            for nation_eng in nations_eng.split(", "):
                datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)              
                nation_ger=datenbank_darsteller.get_nation_eng_to_german(str(nation_eng))      
                index=self.Main.cBox_performer_nation.findText(nation_ger)
                if index == -1 and nation_ger:
                    self.Main.cBox_performer_nation.addItem(nation_ger)
        infos_webside.set_tooltip_text("cBox_performer_", "nation", f"IAFD: {nation_text}", "IAFD")

    def haar_abfrage_iafd(self, content, infos_webside):        
        haar_text=None 
        
        haar_element=content.xpath("//p[contains(string(),'Hair Color')]/following::p[1]")
        haar_text=haar_element[0].text_content() if haar_element else None        
        if haar_text not in (None, "", "No data"):        
            self.Main.lnEdit_performer_haar.setText(haar_text) 
        infos_webside.set_tooltip_text("lnEdit_performer_", "haar", f"IAFD: {haar_text}", "IAFD")

    def gewicht_abfrage_iafd(self, content, infos_webside):        
        gewicht_text=None 
        
        gewicht_element=content.xpath("//p[contains(string(),'Weight')]/following::p[1]")
        gewicht_text=gewicht_element[0].text_content() if gewicht_element else None        
        if gewicht_text not in (None, "", "No data"):
            gewicht_text = re.search(r'lbs \((\d+)', gewicht_text).group(1) if re.search(r'lbs \((\d+)', gewicht_text) else ""
            self.Main.lnEdit_performer_gewicht.setText(f"{gewicht_text} kg") 
        infos_webside.set_tooltip_text("lnEdit_performer_", "gewicht", f"IAFD: {gewicht_text} kg", "IAFD")

    def groesse_abfrage_iafd(self, content, infos_webside):        
        groesse_text=None 
        
        groesse_element=content.xpath("//p[contains(string(),'Height')]/following::p[1]")
        groesse_text=groesse_element[0].text_content() if groesse_element else None        
        if groesse_text not in (None, "", "No data"):
            groesse_text = re.search(r'inches \((\d+)', groesse_text).group(1) if re.search(r'inches \((\d+)', groesse_text) else "N/A"
            self.Main.lnEdit_performer_groesse.setText(f"{groesse_text} cm") 
        infos_webside.set_tooltip_text("lnEdit_performer_", "groesse", f"IAFD: {groesse_text} cm", "IAFD")

    def geburtsort_abfrage_iafd(self, content, infos_webside):        
        geburtsort_text=None 
        
        geburtsort_element=content.xpath("//p[contains(string(),'Birthplace')]/following::p[1]")
        geburtsort_text=geburtsort_element[0].text_content() if geburtsort_element else None        
        if geburtsort_text not in (None, "", "No data"):
            self.Main.lnEdit_performer_geburtsort.setText(f"{geburtsort_text}") 
        infos_webside.set_tooltip_text("lnEdit_performer_", "geburtsort", f"IAFD: {geburtsort_text}", "IAFD")

    def geburtstag_abfrage_iafd(self, content, infos_webside):        
        geburtstag_text=None 
        
        geburtstag_element=content.xpath("//p[contains(string(),'Birthday')]/following::p[1]")
        geburtstag_text=geburtstag_element[0].text_content().strip() if geburtstag_element else None        
        if geburtstag_text not in (None, "", "No data"):
            if " (" in geburtstag_text:
                geburtstag_text, _ = geburtstag_text.split(" (",1)
                geburtstag_text = datetime.strptime(geburtstag_text, "%B %d, %Y").strftime("%d.%m.%Y")
            self.Main.lnEdit_performer_geburtstag.setText(f"{geburtstag_text}") 
        infos_webside.set_tooltip_text("lnEdit_performer_", "geburtstag", f"IAFD: {geburtstag_text}", "IAFD")

    def piercing_abfrage_iafd(self, content, infos_webside):        
        piercing_text="" 
        
        piercing_element=content.xpath("//p[contains(string(),'Piercings')]/following::p[1]")
        piercing_text=piercing_element[0].text_content() if piercing_element else ""      
        if piercing_text:            
            self.Main.txtEdit_performer_piercing.setPlainText(piercing_text) 
        infos_webside.set_tooltip_text("txtEdit_performer_", "piercing", f"IAFD: {piercing_text[:40]}", "IAFD")

    def tattoo_abfrage_iafd(self, content, infos_webside):        
        tattoo_text=""
        
        tattoo_element=content.xpath("//p[contains(string(),'Tattoos')]/following::p[1]")
        tattoo_text=tattoo_element[0].text_content() if tattoo_element else ""        
        if tattoo_text:            
            self.Main.txtEdit_performer_tattoo.setPlainText(tattoo_text) 
        infos_webside.set_tooltip_text("txtEdit_performer_", "tattoo", f"IAFD: {tattoo_text[:40]}", "IAFD")

    def aktiv_abfrage_iafd(self, content, infos_webside):        
        aktiv_text=None 
        
        aktiv_element=content.xpath("//p[contains(string(),'Years Active')]/following::p[1]")
        aktiv_text=aktiv_element[0].text_content() if aktiv_element else None        
        if aktiv_text not in (None, "", "No data"): 
            if " (" in aktiv_text:
                aktiv_text,_=aktiv_text.split(" (",1)
            aktiv = "Ja" if aktiv_text.split("-",1)[1]=="2023" else "Nein"           
            self.Main.lnEdit_performer_aktiv.setText(f"{aktiv} von: {aktiv_text}") 
        infos_webside.set_tooltip_text("lnEdit_performer_", "aktiv", f"IAFD: {aktiv_text}", "IAFD")

    def boobs_abfrage_iafd(self, content, infos_webside):        
        boobs_text=None 
        
        boobs_element=content.xpath("//p[contains(string(),'Measurements')]/following::p[1]")
        boobs_text=boobs_element[0].text_content() if boobs_element else None        
        if boobs_text not in (None, "", "No data"): 
            boobs_text, _ = boobs_text.split("-",1)           
            self.Main.lnEdit_performer_boobs.setText(boobs_text) 
        infos_webside.set_tooltip_text("lnEdit_performer_", "boobs", f"IAFD: {boobs_text}", "IAFD")

    def onlyfans_abfrage_iafd(self, content, infos_webside):        
        onlyfans=[]
        
        onlyfans_elements=content.xpath("//p[contains(string(),'Website')]/following::p/a[@target='starlet']")              
        if onlyfans_elements: 
            for zeile, onlyfans_text in enumerate(onlyfans_elements):
                if onlyfans_text is not None:
                    onlyfans_text=str(onlyfans_text.get('href')) 
                    self.Main.cBox_performer_fanside.addItem(onlyfans_text)
                    onlyfans.append(onlyfans_text)  
                else:
                    break
            onlyfans=", ".join(onlyfans)
        infos_webside.set_tooltip_text("cBox_performer_", "fanside", f"IAFD: {onlyfans}", "IAFD")
    
    def load_and_scale_pixmap(self,image_path, label):
        pixmap = QPixmap()
        if isinstance(image_path, str):
            pixmap.load(str(image_path))
        else:
            pixmap.loadFromData(image_path)        
        label_height = 280
        try:
            label_width = int(label_height * pixmap.width() / pixmap.height())
        except ZeroDivisionError as e:
            print(f"{self.Main.lnEdit_performer_info.text()} --> Fehler: {e}")
            return
        label.setPixmap(pixmap.scaled(label_width, label_height, Qt.AspectRatioMode.KeepAspectRatio))

    def load_image_in_label(self, content):        
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        id = self.Main.grpBox_performer.title().replace("Performer-Info ID: ","") # ArtistID
        name = self.Main.lnEdit_performer_info.text() # Performer 'Name'
        artist_id=0 

        if id.isdigit():
            artist_id=int(id)
        errview, image_pfad = datenbank_darsteller.get_iafd_image(artist_id=artist_id, name=name)

        if not image_pfad:
            image_url = content.xpath("//div[@id='headshot']/img")
            if image_url:
                image_url = image_url[0].get("src")
                response = requests.get(image_url, headers=HEADERS)
                image_data = response.content
                self.load_and_scale_pixmap(image_data, self.Main.lbl_iafd_image)
        else:            
            self.load_and_scale_pixmap(str(PROJECT_PATH / image_pfad), self.Main.lbl_iafd_image)


# Abschluss
if __name__ == '__main__':
    IAFDInfos()