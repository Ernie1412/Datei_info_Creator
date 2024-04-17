from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QFileDialog, QApplication

import sys
import json
from pathlib import Path

from gui.helpers.message_show import MsgBox, StatusBar

from config import EINSTELLUNGEN_JSON_PATH, JSON_PATH
from config import EINSTELLUNG_UI

    ### --------------------------------------------------------------------- ###
    ### -------Einstellungen werden hier global gespeichert ----------------- ###
    ### --------------------------------------------------------------------- ###
class Einstellungen(QDialog):
    def __init__(self, parent=None):
        super(Einstellungen, self).__init__(parent)
        uic.loadUi(EINSTELLUNG_UI, self)
        self.main = parent
        self.Btn_OK.clicked.connect(self.accept_settings)
        self.lade_einstellung()


    def einstellung_save(self, last_directory: str="",exiftool: str=None, webscraping: str=None,save: str=None, theporndb_apikey: str="", tpdb_image_counter: int=0):       
        if Path(EINSTELLUNGEN_JSON_PATH).exists():
            set: dict=json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes())
            exiftool = set["InfosExifTool"] if exiftool is None else exiftool
            webscraping = set["WebScraping"] if webscraping is None else webscraping
            save = set["Speichern"] if save is None else save
            last_directory = set["LastDir"] if last_directory =="" else last_directory
            theporndb_apikey = set["theporndb_apikey"] if theporndb_apikey =="" else theporndb_apikey
            tpdb_image_counter = set["tpdb_image_counter"] if tpdb_image_counter == 0 else tpdb_image_counter
        else:
            MsgBox(self.main, "Einstellungs Datei wurde neu angelegt !","i") 
        
        self.set_settings(last_directory,exiftool,webscraping,save,theporndb_apikey, tpdb_image_counter)

    def set_settings(self, last_directory: str="",exiftool: str=None, webscraping: str=None,save: str=None, theporndb_apikey: str=None, tpdb_image_counter: str=None):
        set={
            "InfosExifTool":exiftool,
            "WebScraping":webscraping,
            "Speichern":save,
            "LastDir":last_directory,
            "theporndb_apikey": theporndb_apikey,
            "tpdb_image_counter": tpdb_image_counter      }            
        json.dump(set, open(EINSTELLUNGEN_JSON_PATH,'w'),indent=4, sort_keys=True)


    def lade_einstellung(self):        
        if not Path(JSON_PATH).exists():
            Path.mkdir(JSON_PATH)
        elif not Path(EINSTELLUNGEN_JSON_PATH).exists():
            self.set_settings()
        else:
            set=json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes())
            self.chkBox_InfosExifTool.setChecked(set["InfosExifTool"])                
            self.chkBox_WebScraping.setChecked(set["WebScraping"])
            self.chkBox_Speichern.setChecked(set["Speichern"])
            self.lbl_LastDIR.setText(set["LastDir"])
            self.lnEdit_theporndb_apikey.setText(set["theporndb_apikey"])
            self.spinBox_tpdb_image_counter.setValue(int(set["tpdb_image_counter"]))
            StatusBar(self.main, "Einstellungen wurde geladen","#efffa7")

    ### Funktion wird von "Main" aufgerufen (directory = einstellungen_ui.get_last_folder())
    def get_last_folder(self) -> Path: 
        set = json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes())            
        dialog = QFileDialog.getExistingDirectory(self,"Ordner öffnen",set["LastDir"])  
        if dialog:
            directory = Path(dialog)   
            if str(directory)!=set["LastDir"]:                
                self.lbl_LastDIR.setText(str(directory))
                self.einstellung_save(str(directory))  
        else: 
            directory = None
        return directory 


    def accept_settings(self):
        if self.chkBox_Speichern.isChecked():
            settings = self.get_settings_from_ui()
            self.einstellung_save(*settings)
            StatusBar(self.main, "Einstellungen gespeichert","#efffa7")#hellgelb)
        else:
            StatusBar(self.main, "KEINE Einstellungen gespeichert !","#ffea9e")#orangegelb)
        self.hide() 

    def get_settings_from_ui(self):
        return [self.lbl_LastDIR.text(),
            self.chkBox_InfosExifTool.isChecked(),
            self.chkBox_WebScraping.isChecked(),
            self.chkBox_Speichern.isChecked(),
            self.lnEdit_theporndb_apikey.text(),
            self.spinBox_tpdb_image_counter.value()
                ]

if __name__ == '__main__':
    app, DialogWindow =(QApplication(sys.argv), Einstellungen())
    DialogWindow.show()   
    sys.exit(app.exec())