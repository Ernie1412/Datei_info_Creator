from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.QtCore import Qt, QEvent

from gui.dialog_socialmedia_link import SocialMediaLink
from gui.custom_cBox_check_icon import CustomComboBoxCheckIcon

from config import SOCIAL_MEDIA_AUSWAHL_UI

class SocialMediaAuswahl(QDialog):
    def __init__(self, *args, **kwargs): # von wo es kommt
        parent = kwargs.pop('parent', None)
        super(SocialMediaAuswahl,self).__init__(parent) 
        self.Main = parent 
        if "type" in kwargs:
            self.type = kwargs["type"]
        if "items_dict" in kwargs:
            self.items_dict = kwargs["items_dict"]
        self.max_labels = 3 # (10 + 1)
       
        uic.loadUi(SOCIAL_MEDIA_AUSWAHL_UI, self)        
        self.setupUi() 

    def setupUi(self):        
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")              
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.accepted.connect(self.accepted_socialmedias)
        self.rejected.connect(self.close)
        self.combobox = getattr(self,f"cBox_{self.type}")
        self.combobox.lineEdit().setPlaceholderText("Auswahl an Sozial Media Links")         
        #combobox.lineEdit().textChanged.connect(combobox.filterItems)        
        self.exec()

    def accepted_socialmedias(self):
        checked_items = getattr(self,f"cBox_{self.type}").get_checked_items()        
        for button_number, (text, icon) in enumerate(checked_items,1):            
            button = getattr(self.Main, f"Btn_performers_{self.type}_{button_number}")
            button.clicked.connect(lambda state, num=button_number:SocialMediaLink(button=str(num), parent=self.Main))
            button.setToolTip(text)
            button.setIcon(icon)
            button.setVisible(True)

if __name__ == '__main__':
    SocialMediaAuswahl(QDialog)