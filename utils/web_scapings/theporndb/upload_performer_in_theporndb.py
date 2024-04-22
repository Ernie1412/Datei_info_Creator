from PyQt6.QtCore import QTimer

from datetime import datetime
import json
import logging
import re

from utils.web_scapings.theporndb.helpers.http import Http
from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper
from gui.dialog_gender_auswahl import GenderAuswahl

from config import PROJECT_PATH

class UploadPerformer():
    def __init__(self, MainWindow, parent): # von wo es kommt 
        self.Main = MainWindow 
        self.scrape_actor_infos = parent
        logging.basicConfig(filename=PROJECT_PATH / "log_files" / "tpdb" / 'uploader_performer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    def upload_performer(self):
        if not self.scrape_actor_infos.chkBox_send_api.isChecked():            
            self.scrape_actor_infos.lbl_status_message.setText("CheckBox 'Upload API' is deaktiviert !")
            QTimer.singleShot(100, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color: #FF0000'))
            QTimer.singleShot(3500, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color:'))
            QTimer.singleShot(5000, lambda: self.scrape_actor_infos.lbl_status_message.setText(""))             
            return
        
        payload = {}                        
        id = self.scrape_actor_infos.lnEdit_performer_id.text()
        payload['id'] = id
        payload['name'] = self.scrape_actor_infos.lnEdit_performer_name.text()
        ### ------------------ payload[extras] --------------------- ### 
        print(self.scrape_actor_infos.Btn_actor_gender_sign.property("upload"))
        if self.scrape_actor_infos.Btn_actor_gender_sign.property("upload"):       
            payload['gender'] = self.get_gender_payload(payload)
        payload = self.get_data_payload(payload)        
        payload = self.get_textedits_payload(payload)        
        payload = self.get_combo_payload(payload)        
        if self.get_links_payload(payload):
            payload = self.get_links_payload(payload)   
        payload = self.get_fakeboobs_payload(payload)     
        ### ------------------- daten übertragen und loggen -------------- ###
        header, status = TPDB_Scraper.get_header()
        if status:
            disp_result = self.post_to_api(payload, header, id)
            self.save_upload_log_file(payload, disp_result) 
        else:
            self.scrape_actor_infos.lbl_status_message.setText("Upload Fehler: Key Falsch !")
            QTimer.singleShot(100, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color: #FF0000'))
            QTimer.singleShot(3500,lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color:'))
       
    def property_mapping(self): 
        return {'birthday': 'lnEdit_performer_birthday',
                'birthplace': 'lnEdit_performer_birthplace',
                'nationality': 'lnEdit_performer_nationality',
                'deathday': 'lnEdit_performer_deathday',                
                'height': 'lnEdit_performer_height',
                'cupsize': 'lnEdit_performer_boobs',
                'height':  'lnEdit_performer_height',
                'weight': 'lnEdit_performer_weight',
                'career_start_year': 'lnEdit_performer_career_start_year',
                'career_end_year': 'lnEdit_performer_career_end_year'}

    def convert(self, value, prop):
        if prop in ['height', 'weight','career_end_year', 'career_start_year']:
            return int(value)
        return value   
    
    def get_data_payload(self, payload):
        for property, widget in self.property_mapping().items():            
            widget = getattr(self.scrape_actor_infos, widget) 
            if widget.activated and widget.text():                
                payload[property] = self.convert(widget.text(), property)
                widget.setActivated(False)
        return payload 

    def get_gender_payload(self, payload):                    
        payload['gender'] = self.scrape_actor_infos.Btn_actor_gender_sign.property("gender")
        self.scrape_actor_infos.Btn_actor_gender_sign.setProperty("upload", False)
        return payload
    
    def property_mapping_for_textedit(self):
        return {'tattoos': 'txtEdit_performer_tattoo',
                'piercings':'txtEdit_performer_piercing'}
    
    def get_textedits_payload(self, payload):
        for property, widget in self.property_mapping_for_textedit().items():            
            widget = getattr(self.scrape_actor_infos, widget) 
            if widget.activated and widget.toPlainText():                
                payload[property] = widget.toPlainText()
                widget.setActivated(False)
        return payload 
    
    def property_mapping_for_combo(self):
        return {'eye_colour': 'eye',
                'ethnicity':'rasse',
                'hair_colour':'hair',
                "birthplace_code": 'nation_code'}
    def get_combo_payload(self, payload):
        for property, widget in self.property_mapping_for_combo().items():            
            combobox = getattr(self.scrape_actor_infos,f"cBox_performer_{widget}")
            checkbox = getattr(self.scrape_actor_infos,f"chkBox_actor_{widget}")  
            if checkbox.isChecked() and combobox.currentText():
                if property == 'birthplace_code':
                    cleaned = re.sub(r'^.+?\(', '', combobox.currentText())[:-1] 
                    payload[property] = cleaned
                else:
                    payload[property] = combobox.currentText()
                checkbox.setChecked(False) 
                combobox.setStyleSheet("background-color: #FFFDD5;")              
        return payload
    
    def get_fakeboobs_payload(self, payload):
        if self.scrape_actor_infos.chkBox_fake_boobs.isChecked():
            payload['fake_boobs'] = True       
        return payload
    
    def get_links_payload(self, payload):
        links ={}        
        for row in range(self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.rowCount()):
            name = self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.item(row, 0)
            link = self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.item(row, 1)
            links[name.text()] = link.text()
        payload['links'] = links
        if not links:
            payload = None
        return payload
    
    def get_ethnicity_payload(self, payload):       
        if self.scrape_actor_infos.chkBox_actor_ethnicity.isChecked():
            payload['ethnicity'] = self.scrape_actor_infos.cBox_performer_rasse.currentText()
        return payload
    
    def get_table_link_from_api(self):
        data_list = ["-----------------------------------------------------",]
        for row in range(self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.rowCount()):
            link = self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.item(row, 1).text()
            if link:
                data_list.append(link)            
        return data_list

    def save_upload_log_file(self, payload, disp_result):        
        now = datetime.now()
        upload = {}
        date_stamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        filename = date_stamp + '_upload.log'          
        payload['upload_log'] =f"{date_stamp}: {disp_result}"
        payload['api_table'] = self.get_table_link_from_api()

        with open(PROJECT_PATH / "log_files" / "tpdb" / filename, 'w') as f:
            json.dump(payload, f)         
        
        self.scrape_actor_infos.lbl_status_message.setText(f"Upload Logfile erstellt: Zeit: {date_stamp}, Status: {disp_result}")
        if 'Submitted OK' in disp_result:
            QTimer.singleShot(100, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color: #90EE90'))
            QTimer.singleShot(3500, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color:'))  
        else:
            QTimer.singleShot(100, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color: #FF0000'))
            QTimer.singleShot(3500, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color:'))

        

    def post_to_api(self, payload, headers, uuid):
        disp_result = ""

        response = Http.post(f'https://theporndb.net/performers/{uuid}/edit', json=payload, headers=headers, timeout=7)        
        if response is not None:
            if response.ok:
                disp_result = f'{disp_result} Submitted OK'
            else:
                disp_result = f'{disp_result} Submission Error: Code #{response.status_code} / {response.reason}'
        else:
            disp_result = f'{disp_result} Submission Error: No Response Code'            
            if response:
                logging.info(response.content)
        return disp_result
            