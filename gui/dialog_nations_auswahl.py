from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from utils.database_settings.database_for_darsteller import DB_Darsteller

from config import NATIONS_AUSWAHL_UI

class NationsAuswahl(QDialog):
    def __init__(self, parent): # von wo es kommt
        super(NationsAuswahl,self).__init__(parent) 
        self.Main = parent         
        self.max_labels = 8 # (7 + 1)        
       
        uic.loadUi(NATIONS_AUSWAHL_UI, self)                
        self.setupUi() 

    def setupUi(self):        
        self.cBox_nations.addItems("Nation", self.get_all_nations_from_db(), DB_Darsteller(self.Main))
        self.set_checked_nations()
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")                
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.accepted.connect(self.accepted_nations)
        self.rejected.connect(self.close)         
        self.exec()

    def get_all_nations_from_db(self):
        datenbank_darsteller = DB_Darsteller(self.Main)
        all_nations = []
        for nation in datenbank_darsteller.get_all_nations_ger():
            all_nations.append(nation)
        return all_nations

    def accepted_nations(self):
        self.Main.Btn_DBArtist_Update.setEnabled(True)
        self.clear_all_nations_labels()
        checked_items = self.cBox_nations.get_checked_items()        
        for widget_number, text in enumerate(checked_items, 1):            
            label = getattr(self.Main, f"lbl_performer_nation_{widget_number}")                        
            label.setStyleSheet(f"background-image: {self.cBox_nations.get_icon(text)}")            
            label.setToolTip(text) 
    
    def set_checked_nations(self):        
        for widget_number in range(1, self.max_labels):
            nation = getattr(self.Main, f"lbl_performer_nation_{widget_number}").toolTip().split(": ")
            if len(nation) > 1: 
                index = self.cBox_nations.findText(nation[1])               
                self.cBox_nations.setChecked(index)

    def clear_all_nations_labels(self) -> None:
        for widget_number in range(1, self.max_labels):            
            widget = getattr(self.Main, f"lbl_performer_nation_{widget_number}", None)
            if widget: 
                widget.setProperty("nation","")
                widget.setStyleSheet("")  
                widget.setToolTip("")
    
if __name__ == '__main__':
    NationsAuswahl(QDialog)