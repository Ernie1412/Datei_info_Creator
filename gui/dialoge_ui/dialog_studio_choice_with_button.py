from PyQt6 import uic
from PyQt6.QtWidgets import QPushButton, QDialog
from PyQt6.QtGui import QIcon

from utils.database_settings.database_for_settings import Webside_Settings

from config import STUDIO_CHOICE_UI

import gui.resource_collection_files.studios_rc

class StudioChoiceButton(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.Main = parent
        uic.loadUi(STUDIO_CHOICE_UI, self)   
        self.clicked_button = self.Main.sender()
        
        website_settings = Webside_Settings(self.Main)
        buttons = website_settings.get_all_studios_from_settingdb()              
        for button in buttons: 
            try:                          
                self.findChild(QPushButton, f'Btn_{button}').clicked.connect(self.set_button_in__main_tab)
            except AttributeError:
                pass
        if self.clicked_button.objectName().startswith("Btn_"):            
            self.show()
        
    def set_button_in__main_tab(self):        
        logo_button = self.sender()                             
        studio = logo_button.whatsThis()
        print(studio)   
        icon_logo = logo_button.icon()  
        if self.clicked_button.objectName() in ["Btn_logo_am_infos_tab", "Btn_logo_am_analyse_tab"]: 
            self.Main.cBox_studio_links.clear()           
            self.Main.Btn_logo_am_infos_tab.setToolTip(studio)
            self.Main.Btn_logo_am_infos_tab.setIcon(icon_logo)
            self.Main.Btn_logo_am_analyse_tab.setToolTip(studio)
            self.Main.Btn_logo_am_analyse_tab.setIcon(icon_logo)             
            self.Main.lnEdit_Studio.setText(studio)
            self.Main.lbl_SuchStudio.setText(studio)                
            self.Main.Btn_VideoDatenHolen.setEnabled(True)
            self.Main.lnEdit_Studio.setText(studio)
            if not studio:            
                self.Main.Btn_VideoDatenHolen.setEnabled(False)
                self.Main.lnEdit_Studio.setText("")             
        else: 
            self.Main.set_database_tab_enabled(icon_logo, studio)   
        self.accept()

    def get_icon_for_studio(self, studio_name):
        website_settings = Webside_Settings(self.Main)        
        network = website_settings.get_network_for_studio(studio_name)
        if not network:
            return None, None
        site_or_network = f"site{network}" if studio_name == network else f"network{network}/{studio_name}"
        icon_qrc = f":/studios/{site_or_network}/{studio_name}_90x40.png"  
        print(icon_qrc, studio_name, network)      
        return studio_name, QIcon(icon_qrc)

if __name__ == "__main__":
    StudioChoiceButton(QDialog)