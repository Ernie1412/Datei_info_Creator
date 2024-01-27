from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from gui.clearing_widgets import ClearingWidget

from config import SOCIAL_MEDIA_LINK_UI

class SocialMediaLink(QDialog):

    def __init__(self, parent, button): # von wo es kommt 
        super(SocialMediaLink,self).__init__(parent) 
        self.Main = parent 
        self.button = button
       
        uic.loadUi(SOCIAL_MEDIA_LINK_UI, self)        
        self.accepted.connect(self.accepted_socialmedia_link) 
        self.rejected.connect(self.close)       
        self.Btn_socialmedia_del.clicked.connect(self.delete_socialmedia_link)
        icon, button_link=self.get_icon_text_from_main_window(button)
        self.lbl_socialmedia_icon.setPixmap(QPixmap(icon.pixmap(25, 25)))
        self.lnEdit_socialmedia_link.setText(button_link)
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")              
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)                 
        self.exec()

    def accepted_socialmedia_link(self):
        zahl = int(self.button)
        social_media_link = self.lnEdit_socialmedia_link.text()
        value = self.get_socialmedia_icon(social_media_link)
        self.Main.set_socialmedia_in_button(social_media_link, value, zahl)
        self.close()

    def get_socialmedia_icon(self, social_media_link):
        social_media_dict = self.Main.get_social_media_dict()
        for key, value in social_media_dict.items():
            if key in social_media_link:
                return value
        return "www"            

    def delete_socialmedia_link(self):
        zahl=int(self.button)
        index=1        
        while getattr(self.Main, f"Btn_performers_socialmedia_{index}").isVisible():
            if index == zahl:
                button = getattr(self.Main, f"Btn_performers_socialmedia_{index}")                 
                index_shift = self.shift_other_buttons(index, button) 
                ClearingWidget(self.Main).clear_social_media(index_shift)
                self.close()
            index += 1
        self.close()

    def shift_other_buttons(self, index: int, button_name_delete: QPushButton):
        while getattr(self.Main, f"Btn_performers_socialmedia_{index+1}").isVisible():            
            button_name_next = getattr(self.Main,f"Btn_performers_socialmedia_{index+1}")            
            button_name_delete.setToolTip(button_name_next.toolTip())
            button_name_delete.setIcon(button_name_next.icon()) 
            index += 1         
        return index
    
    def get_icon_text_from_main_window(self, button): 
        button_name = getattr(self.Main,f"Btn_performers_socialmedia_{button}")
        return button_name.icon(), button_name.toolTip()        

if __name__ == '__main__':
    SocialMediaLink(QDialog)