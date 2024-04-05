from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

import pyperclip

from utils.web_scapings.theporndb.scrape_actor_infos import ScrapeActorInfos

class CustomMenuButtons(QMenu):
    def __init__(self, MainWindow):
        super(CustomMenuButtons).__init__() 
        self.Main = MainWindow
        
    def show_context_menu(self, widget,  pos: int) -> None: 
        widget_name = widget.objectName().replace("Btn_performer_in_", "")
        self.context_menu = QMenu(self.Main)
        menu_dict = {
            f"Add URL für {widget_name}": lambda: self.add_url(widget_name),
            f"Copy Ablage für {widget_name}": lambda: self.clipbboard_url(widget_name),
            f"Scrape {widget_name}": lambda: self.open_api_dialog(widget_name, pos),
            f"Suche in {widget_name}": lambda: self.search_actor_api_dialog(widget_name, pos),
        }
        for menu, func in menu_dict.items():              
            action = QAction(menu, self.Main)            
            action.triggered.connect(func)                
            self.context_menu.addAction(action)
        self.context_menu.addAction(action) 

        self.context_menu.setStyleSheet("QMenu::item:disabled {background: transparent;}")
        self.context_menu.exec(pos)             

    def add_url(self, widget_name):
        print(widget_name)

    def clipbboard_url(self, widget_name):
        text = getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip()
        self.Main.lbl_db_status.setText(f"{text} in Zwischenablage kopiert")
        pyperclip.copy(text)

    def open_api_dialog(self, widget_name, pos):
        if widget_name != self.Main.get_bio_websites(True)[1]: # 1 = ThePornDB
            self.Main.lbl_db_status.setText(f"Fenster für {widget_name} nicht verfügbar !")
            return
        elif getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip() == "":
            self.Main.lbl_db_status.setText(f"Für {widget_name} ist kein Link vorhanden !")
            return
        api_link = getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip()
        dialog = ScrapeActorInfos(api_link, parent=self.Main) 
        dialog.setParent(self.Main)  
        dialog.move(pos.x()-150, pos.y() + 20)
        dialog.exec()

    def search_actor_api_dialog(self, widget_name, pos):
        if widget_name != self.Main.get_bio_websites(True)[1]: # 1 = ThePornDB
            self.Main.lbl_db_status.setText(f"Fenster für {widget_name} nicht verfügbar !")
            return
        elif self.Main.lnEdit_performer_info.text() == "":
            self.Main.lbl_db_status.setText(f"Kein Namen angebene, ist leer !")
            return
        search_name = self.Main.lnEdit_performer_info.text()
        dialog = ScrapeActorInfos(search_name, parent=self.Main) 
        dialog.setParent(self.Main) 
        dialog.move(pos.x()-150, pos.y() + 20)
        dialog.exec()

        
