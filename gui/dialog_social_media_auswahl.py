from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.QtCore import Qt, QEvent

from gui.dialog_socialmedia_link import SocialMediaLink
from gui.helpers.message_show import StatusBar

from gui.get_avaible_labels import GetLabels

from config import SOCIAL_MEDIA_AUSWAHL_UI

class SocialMediaAuswahl(QDialog):
    def __init__(self, *args, **kwargs): # von wo es kommt
        parent = kwargs.pop('parent', None)
        super(SocialMediaAuswahl,self).__init__(parent) 
        self.Main = parent
        if "items_dict" in kwargs:
            self.items_dict = kwargs["items_dict"]
        self.maxlabels = GetLabels().get_avaible_socialmedia_buttons(self.Main,"Btn_performers_socialmedia_")      
        uic.loadUi(SOCIAL_MEDIA_AUSWAHL_UI, self)        
        self.setupUi() 

    def setupUi(self):
        self.lbl_maxlabels.setVisible(False)       
        self.cBox_socialmedia.addItems(self.Main, self.Main.get_social_media_dict())              
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")              
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) 
        self.cBox_socialmedia.setPlaceholderText("Auswahl an Sozial Media Links")
        self.accepted.connect(self.accepted_socialmedias)
        self.rejected.connect(self.close)                 

    def accepted_socialmedias(self):        
        checked_items = self.cBox_socialmedia.get_checked_items()
        button_number = 0
        while button_number <= self.maxlabels and checked_items:
            button = getattr(self.Main, f"Btn_performers_socialmedia_{button_number}")
            if not button.isVisible():
                text, icon = checked_items.pop(0)  # Entferne das erste Element aus der Liste
                try:
                    button.clicked.disconnect()            
                except TypeError:
                    pass
                button.clicked.connect(lambda state, num=button_number: SocialMediaLink(button=str(num), parent=self.Main).exec())
                button.setToolTip(text)
                button.setIcon(icon)
                button.setVisible(True)
                self.Main.Btn_DBArtist_Update.setEnabled(True)
            button_number += 1
        if button_number > self.maxlabels:
            StatusBar(self.Main, "Maximale Anzahl von Buttons erreicht", "#F78181")
           

if __name__ == '__main__':
    SocialMediaAuswahl(QDialog)