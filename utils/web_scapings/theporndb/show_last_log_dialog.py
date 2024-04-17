from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
from PyQt6.QtCore import Qt

import json
from datetime import datetime

from config import SHOW_LOG_DIALOG_THEPORNDB_UI, LOG_THEPORNDB_JSON_FOLDER


class ShowLogDialogThePornDB(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)        
        uic.loadUi(SHOW_LOG_DIALOG_THEPORNDB_UI, self)        
        #self.setWindowFlags(Qt.WindowType.WindowMinMaxButtonsHint) 
        self.Btn_accept.clicked.connect(self.accept)
        self.read_last_log_file()
        self.show()

    def read_last_log_file(self):
        
        logfile = self.get_last_log_file()
        self.lbl_log_file.setText(f"Log Datei: {logfile.name}")

        text = json.loads((LOG_THEPORNDB_JSON_FOLDER / logfile).read_bytes())
        self.txtBrw_logfile.setHtml(self.formated_data_text(text))

    def formated_data_text(self, data):
        text = f"<font color=#000000>{data.get('id', '/')}</font><br>"
        text += f"<font color=#0180FF>{data.get('name', '/')}</font><br>"
        for extra in self.get_properties():
            if extra in data:
                text += f"<font color=#000000>{extra}: </font><b><font color=#098A2A>{data[extra]}</font><br></b>"        
        text += "<b>Links:</b><br>"
        for site, url in data['links'].items():
            text += f"<font color=#000000>{site}: </font><b><font color=#380A60>{url}</font><br></b>"
        for links in data['api_table']:
            text += f"<font color=#2E2EFE>{links}</font><br></b>"
        text += "<br>"
        if 'Submission Error' in data['upload_log']:
            text += f"<b><font color=#E22103>{data['upload_log']}<br></font>"
        else:
            text += f"<b><font color=#03B404>Submitted OK<br></font>"
        return text
    
    def get_properties(self):
        return ['birthplace', 'eye_colour', 'birthday', 'nationality', 'fake_boobs', 'hair_colour', 'cupsize', 'weight', 'career_start_year', 'career_end_year', 'height', 'cupsize', 'ethnicity', 'tattoos', 'piercings']
    
    def get_last_log_file(self):
        log_files = LOG_THEPORNDB_JSON_FOLDER.glob("*.log")
        get_created = lambda f: datetime.fromtimestamp(f.stat().st_ctime)
        log_files = sorted(log_files, key=get_created, reverse=True) 
        return log_files[0]
        


        
if __name__ == '__main__':
    ShowLogDialogThePornDB(QDialog)    
