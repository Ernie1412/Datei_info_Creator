from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.QtCore import Qt, QEvent

from gui.dialog_socialmedia_link import SocialMediaLink
from gui.dialoge_ui.message_show import StatusBar

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
        self.max_labels = 10 # 0-9 +1       
        uic.loadUi(SOCIAL_MEDIA_AUSWAHL_UI, self)        
        self.setupUi() 

    def setupUi(self):
        self.accepted.connect(self.accepted_socialmedias)
        self.rejected.connect(self.close)        
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")              
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)        
        self.combobox = getattr(self,f"cBox_{self.type}")
        self.combobox.lineEdit().setPlaceholderText("Auswahl an Sozial Media Links")
        self.exec()

    def accepted_socialmedias(self):
        checked_items = getattr(self, f"cBox_{self.type}").get_checked_items()
        button_number = 0
        while button_number <= self.max_labels and checked_items:
            button = getattr(self.Main, f"Btn_performers_{self.type}_{button_number}")
            if not button.isVisible():
                text, icon = checked_items.pop(0)  # Entferne das erste Element aus der Liste
                button.clicked.connect(lambda state, num=button_number: SocialMediaLink(button=str(num), parent=self.Main))
                button.setToolTip(text)
                button.setIcon(icon)
                button.setVisible(True)
                self.Main.Btn_DBArtist_Update.setEnabled(True)
            button_number += 1
        if button_number > self.max_labels:
            StatusBar(self.Main, "Maximale Anzahl von Buttons erreicht", "#F78181")
           

if __name__ == '__main__':
    SocialMediaAuswahl(QDialog)