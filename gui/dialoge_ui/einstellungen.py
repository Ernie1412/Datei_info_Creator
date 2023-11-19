from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QFileDialog, QApplication

import sys
import json
from pathlib import Path

from gui.dialoge_ui.message_show import MsgBox, StatusBar

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
        self.Btn_OK.clicked.connect(self.Zurueck)
        self.lade_einstellung()


    def einstellung_save(self, last_directory: str="",exiftool: str=None, webscraping: str=None,save: str=None):       
        if Path(EINSTELLUNGEN_JSON_PATH).exists():
            set: dict=json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes())
            exiftool = set["InfosExifTool"] if exiftool is None else exiftool
            webscraping = set["WebScraping"] if webscraping is None else webscraping
            save = set["Speichern"] if save is None else save
            last_directory = set["LastDir"] if last_directory =="" else last_directory
        else:
            MsgBox(self.main, "Einstellungs Datei wurde neu angelegt !","i") 

        set={
            "InfosExifTool":exiftool,
            "WebScraping":webscraping,
            "Speichern":save,
            "LastDir":last_directory       }            
        json.dump(set, open(EINSTELLUNGEN_JSON_PATH,'w'),indent=4, sort_keys=True)


    def lade_einstellung(self):        
        if not Path(JSON_PATH).exists():
            Path.mkdir(JSON_PATH)

        self.einstellung_save() 

        set=json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes())
        self.chkBox_InfosExifTool.setChecked(set["InfosExifTool"])                
        self.chkBox_WebScraping.setChecked(set["WebScraping"])
        self.chkBox_Speichern.setChecked(set["Speichern"])
        self.lbl_LastDIR.setText(set["LastDir"])
        StatusBar(self.main, "Einstellungen wurde geladen","#efffa7")


    def Info_Datei(self) -> Path:
        set = json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes())            
        dialog = QFileDialog.getExistingDirectory(self,"Ordner öffnen",set["LastDir"])  
        if dialog:
            directory = Path(dialog)   
            if str(directory)!=set["LastDir"]:
                self.einstellung_save(str(directory))
                self.lbl_LastDIR.setText(str(directory))            
        else: 
            directory = None
        return directory 


    def Zurueck(self):
        if self.chkBox_Speichern.isChecked():
            self.einstellung_save("",
                self.chkBox_InfosExifTool.isChecked(),
                self.chkBox_WebScraping.isChecked(),
                self.chkBox_Speichern.isChecked(),
                )
            StatusBar(self.main, "Einstellungen gespeichert","#efffa7")#hellgelb)
        else:
            StatusBar(self.main, "KEINE Einstellungen gespeichert !","#ffea9e")#orangegelb)
        self.hide()  


if __name__ == '__main__':
    app, DialogWindow =(QApplication(sys.argv), Einstellungen())
    DialogWindow.show()   
    sys.exit(app.exec())