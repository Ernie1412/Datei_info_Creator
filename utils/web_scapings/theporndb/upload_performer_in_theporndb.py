from PyQt6.QtCore import QTimer

from datetime import datetime
import json
import logging

from utils.web_scapings.theporndb.helpers.http import Http
from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper

from config import PROJECT_PATH

FOLDER = PROJECT_PATH / "log_files" / "tpdb"

class UploadPerformer():
    def __init__(self, MainWindow, parent): # von wo es kommt 
        self.Main = MainWindow 
        self.scrape_actor_infos = parent
        logging.basicConfig(filename=FOLDER / 'uploader_performer.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    def upload_performer(self):
        if not self.scrape_actor_infos.chkBox_send_api.isChecked():            
            self.scrape_actor_infos.lbl_status_message.setText("CheckBox 'Upload API' is deaktiviert !")
            QTimer.singleShot(100, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color: #FF0000'))
            QTimer.singleShot(3500, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color:'))
            QTimer.singleShot(5000, lambda: self.scrape_actor_infos.lbl_status_message.setText(""))             
            return
        
        payload = {}                
        uuid = self.scrape_actor_infos.lnEdit_performer_uuid.text()
        payload['id'] = uuid
        payload['name'] = self.scrape_actor_infos.lnEdit_performer_name.text()
        ### ------------------ payload[extras] --------------------- ###
        extras = {}
        extras['gender'] = self.scrape_actor_infos.lbl_actor_gender_sign.property("gender")
        extras = self.get_data_extras(extras)        
        extras = self.get_tattoos_extras(extras)
        extras = self.get_piercings_extras(extras)
        # extras = self.get_links_extras(extras)
        payload['extras'] = extras 
        ### ------------------- daten übertragen und loggen -------------- ###
        header, status = TPDB_Scraper.get_header()
        if status:
            disp_result = self.post_to_api(payload, header, uuid)
            self.save_upload_log_file(payload, disp_result) 
        else:
            self.scrape_actor_infos.lbl_status_message.setText("Upload Fehler: Key Falsch !")
            QTimer.singleShot(100, lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color: #FF0000'))
            QTimer.singleShot(3500,lambda: self.scrape_actor_infos.lbl_status_message.setStyleSheet('background-color:'))

    def get_artor_properties(self):
        return ['birthday', 'birthplace', 'nationality', 'hair', 'eye', 'weight', 'height', 'boobs']
    
    def get_data_extras(self, extras):
        for property in self.get_artor_properties():            
            widget = getattr(self.scrape_actor_infos,f"lnEdit_performer_{property}") 
            if widget.activated and widget.text():
                if property == 'boobs':
                    property ='cupsize'
                extras[property] = widget.text()
        return extras  
    
    def get_tattoos_extras(self, extras):
        widget = self.scrape_actor_infos.txtEdit_performer_tattoo        
        if widget.activated and widget.toPlainText():
            extras['tattoos'] = widget.toPlainText()
        return extras
    
    def get_piercings_extras(self, extras):
        widget = self.scrape_actor_infos.txtEdit_performer_piercing       
        if widget.activated and widget.toPlainText():
            extras['tattoos'] = widget.toPlainText()
        return extras
    
    def get_links_extras(self, extras):
        pass

    def save_upload_log_file(self, payload, disp_result):        
        now = datetime.now()
        upload = {}
        date_stamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        filename = date_stamp + '_upload.log'
        upload['upload_log'] = date_stamp
        upload['upload_log'] = disp_result
        payload['upload_log'] = upload
        with open(FOLDER / filename, 'w') as f:
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

        response = Http.post(f'https://api.theporndb.net/performers/{uuid}', json=payload, headers=headers, timeout=5)        
        if response is None:
            if response.ok:
                disp_result = f'{disp_result} Submitted OK'
            else:
                disp_result = f'{disp_result} Submission Error: Code #{response.text}'
        else:
            disp_result = f'{disp_result} Submission Error: No Response Code'            
            if response:
                logging.info(response.content)
        return disp_result
            