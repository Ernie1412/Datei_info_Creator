from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import requests
from lxml import html

import pyperclip
import json
import re
from datetime import datetime

from gui.helpers.socialmedia_buttons import SocialMediaButtons
from gui.helpers.set_tootip_text import SetTooltipText
from gui.helpers.check_new_performer_infos import CheckNewPerformerInfos
from utils.database_settings.database_for_darsteller import DB_Darsteller

from config import HEADERS, PROJECT_PATH

class ScapeBabePediaPerformer():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow

    def get_babepedia_performer_link(self):
        name=self.Main.customlnEdit_babepedia_performer.text().lower().strip()
        cbox_sex=self.Main.cBox_performer_sex.currentText()
        sex = self.dict_sex(cbox_sex,cbox=True)
        babepedia_link = None 
        if sex:            
            name=name.replace(" ","_")            
            babepedia_link=f"https://www.babepedia.com/babe/{name}"
            self.Main.lnEdit_DBBioWebsite_artistLink.setText(babepedia_link)            
            pyperclip.copy(babepedia_link)
        return babepedia_link
   
    def check_babepedia_performer_link(self, link):                 
        if link.startswith("https://www.babepedia.com/babe/"):
            try:                    
                r = requests.get(link, headers=HEADERS, timeout=10)
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:                
                return e
            else:
                content = html.fromstring(r.content)
                elements = content.xpath("//h1[@id='babename']")    
                if elements:                
                    return True
                else:
                    return False 
                
    def load_babepedia_performer_link(self, link):        
        tooltip_text = SetTooltipText(self.Main)   
        check_performer_infos = CheckNewPerformerInfos(self.Main)     
        
        if link is None:
            return        
        try:
            response = requests.get(link, headers=HEADERS, timeout=10)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:            
            status = e           
        else:
            content = html.fromstring(response.content)              
             
            #self.sex_abfrage_babepedia(tooltip_text, check_performer_infos)
            self.rasse_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.augen_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.body_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.haar_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.gewicht_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.groesse_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.geburtsort_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.geburtstag_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.piercing_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.tattoo_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.aktiv_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.boobs_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.onlyfans_abfrage_babepedia(content, tooltip_text, check_performer_infos)
            self.load_image_in_label(content)
            
    def set_tooltip_and_check_infos(self, type, value, tooltip_text, check_performer_infos):
        if type in ['eye', 'rasse']:
            tooltip_text.set_tooltip_text("cBox_performer_", type, f"BabePedia: {value}", "BabePedia")
        elif type in ['tattoo', 'piercing']:
            tooltip_text.set_tooltip_text("txtEdit_performer_", type, f"BabePedia: {value}", "BabePedia")
        else:
            tooltip_text.set_tooltip_text("lnEdit_performer_", type, f"BabePedia: {value}", "BabePedia")
        check_performer_infos.check_selections_count(type, value)

    def sex_abfrage_babepedia(self, tooltip_text, check_performer_infos):
        tooltip_text.set_tooltip_text("Btn_performers_gender", "gender", f"BabePedia: weiblich", "BabePedia")
    
    def rasse_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):
        type="rasse"

        rasse_element = content.xpath("//li[contains(string(),'Ethnicity:')]/text()")
        value = rasse_element[0].strip() if rasse_element else None                    
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def augen_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):
        type="eye"

        eye_element = content.xpath("//li[contains(string(),'Eye color:')]//text()")
        value = eye_element[2].strip() if eye_element else None 
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def body_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):
        type="body"
        
        body_element=content.xpath("//li[contains(string(),'Body type')]/text()")
        value = body_element[0].strip() if body_element else None        
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def haar_abfrage_babepedia(self, content, tooltip_text, check_performer_infos): 
        type="hair"

        haar_element=content.xpath("//li[contains(string(),'Hair color:')]//text()")
        value = haar_element[2].strip() if haar_element else None        
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def gewicht_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        type="weight" 
        
        gewicht_element=content.xpath("//li[contains(string(),'Weight:')]/text()")
        value = gewicht_element[0].strip() if gewicht_element else None        
        if value:
            value = re.findall(r'\d+', value)[-1]
            self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def groesse_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        type="height" 
        
        groesse_element=content.xpath("//li[contains(string(),'Height:')]/text()")
        value = groesse_element[0].strip() if groesse_element else None        
        if value:
            value = re.findall(r'\d+', value)[-1]
            self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def geburtsort_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        type="birthplace" 
        
        geburtsort_element=content.xpath("//li[contains(span, 'Birthplace')]//text()")
        value = geburtsort_element[1].strip(":")+geburtsort_element[2] if geburtsort_element else None 
        self.set_tooltip_and_check_infos(type, value.strip(), tooltip_text, check_performer_infos)

    def geburtstag_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        type="birthday" 
        
        geburtstag_element=content.xpath("//li[contains(string(),'Born')]/a/text()")
        date_string=f"{geburtstag_element[0]} {geburtstag_element[1]}" if geburtstag_element else None        
        if date_string:
            geburtstag_text = cleaned_date_string = re.sub(r'\b(\d+)(st|nd|rd|th)\b', r'\1', date_string)            
            geburtstag_text = datetime.strptime(geburtstag_text, "%d of %B %Y").strftime("%d.%m.%Y")
            self.set_tooltip_and_check_infos(type, geburtstag_text, tooltip_text, check_performer_infos)

    def piercing_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        type="piercing" 
        
        piercing_element=content.xpath("//li[contains(string(),'Piercings')]/a/text()")
        value = piercing_element[0].strip() if piercing_element else ""      
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def tattoo_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        type="tattoo"
        
        tattoo_element=content.xpath("//li[contains(string(),'Tattoos')]/a/text()")
        value = tattoo_element[0].strip() if tattoo_element else ""        
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def aktiv_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):
        type="activ"
        
        activ_element=content.xpath("//li[contains(string(),'Years active:')]/a/text()")
        value = activ_element[0].strip() if activ_element else ""        
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def boobs_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        type="boobs" 
   
        boobs_element=content.xpath("//li[contains(string(),'Bra/cup size:')]/a/text()")
        value = boobs_element[0].strip() if boobs_element else None        
        self.set_tooltip_and_check_infos(type, value, tooltip_text, check_performer_infos)

    def onlyfans_abfrage_babepedia(self, content, tooltip_text, check_performer_infos):        
        onlyfans=[]
        
        onlyfans_elements=content.xpath("//div[@id='socialicons']/a")              
        if onlyfans_elements: 
            for zeile, onlyfans_text in enumerate(onlyfans_elements):
                if len(onlyfans_text):
                    onlyfans_text=str(onlyfans_text.get('href'))
                    onlyfans.append(onlyfans_text.lower())  
                else:
                    break        
        self.add_socialmedia_button(onlyfans)
    
    def add_socialmedia_button(self, onlyfans):        
        db_socialmedias = SocialMediaButtons.get_social_media_from_buttons(self.Main)
        diff = list(set(onlyfans) - set(db_socialmedias))
        social_medias = "\n".join(diff)
        self.Main.set_social_media_in_buttons(social_medias, len(db_socialmedias))
    
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
        id = self.Main.grpBox_performer_name.title().replace("Performer-Info ID: ","") # ArtistID        
        image_pfad: str=None  

        if id.isdigit():
            artist_id = int(id)
            image_pfad = datenbank_darsteller.get_biowebsite_image("BabePedia", artist_id)

        if not image_pfad:
            image_url = content.xpath("//div[@id='profimg']/a")
            if image_url:
                baselink = 'https://www.babepedia.com'
                image_url = image_url[0].get("href")
                name = re.sub(r'image.*', '', image_url[0].get("alt"))
                if 'javascript:alert' in image_url:
                    self.Main.lbl_db_status.setText(f"Kein Bild gefunden für {self.Main.grpBox_performer_name.title()}")
                    return
                response = requests.get(baselink + image_url, headers=HEADERS)
                image_data = response.content
                label = self.Main.lbl_BabePedia_image
                self.load_and_scale_pixmap(image_data, label)
                label.setProperty("name", name)
                label.setToolTip(f"{baselink}{image_url}")
                self.Main.Btn_DBArtist_Update.setEnabled(True)
        else:            
            self.load_and_scale_pixmap(str(PROJECT_PATH / image_pfad), self.Main.lbl_BabePedia_image)


# Abschluss
if __name__ == '__main__':
    ScapeBabePediaPerformer()