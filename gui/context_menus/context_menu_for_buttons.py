from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

import pyperclip

from utils.web_scapings.theporndb.scrape_actor_infos import ScrapeActorInfos
from utils.web_scapings.babepedia.scrape_babepedia_performer import ScapeBabePediaPerformer
from utils.web_scapings.helpers.helpers import CheckBioWebsiteStatus


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
            f"zeige letzte Logfile für {widget_name} an": lambda: self.show_last_logfile(pos),
        }
        for menu, func in menu_dict.items():              
            action = QAction(menu, self.Main)            
            action.triggered.connect(func)                
            self.context_menu.addAction(action)
        self.context_menu.addAction(action) 

        self.context_menu.setStyleSheet("QMenu::item:disabled {background: transparent;}")
        self.context_menu.exec(pos)             

    def add_url(self, widget_name):
        if widget_name == "BabePedia":
            link = f"https://www.babepedia.com/babe/{self.Main.lnEdit_performer_info.text().replace(' ','_')}"            
            scrape_bapepedia_performer = ScapeBabePediaPerformer(self.Main)
            if scrape_bapepedia_performer.check_babepedia_performer_link(link):
                self.Main.Btn_performer_in_BabePedia.setToolTip(link)
                self.Main.lbl_db_status.setText(f"URL für {widget_name} hinzugefügt")
                self.Main.set_biobutton_state(widget_name, True)
            else:
                self.Main.lbl_db_status.setText(f"Name für {widget_name} nicht gefunden !")
                self.Main.set_biobutton_state(widget_name, False)

    def clipbboard_url(self, widget_name):
        text = getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip()
        self.Main.lbl_db_status.setText(f"{text} in Zwischenablage kopiert")
        pyperclip.copy(text)

    def open_api_dialog(self, widget_name, pos):
        self.Main.lnEdit_DBWebSite_artistLink.setText(getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip())
        if widget_name == self.Main.get_bio_websites(True)[0]: # 0 = IAFD
            self.Main.load_IAFD_performer_link()
        elif widget_name == self.Main.get_bio_websites(True)[1]: # 1 = BabePedia
            self.scrape_babepedia(widget_name)
        elif widget_name == self.Main.get_bio_websites(True)[2]: # 2 = ThePornDB
            self.scrape_the_porn_db(widget_name, pos) 
        elif getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip() == "":
            self.Main.lbl_db_status.setText(f"Für {widget_name} ist kein Link vorhanden !")
            return
        self.Main.lbl_db_status.setText(f"Fenster für {widget_name} nicht verfügbar !")


    def search_actor_api_dialog(self, widget_name, pos):
        if widget_name != self.Main.get_bio_websites(True)[1]: # 1 = ThePornDB
            self.Main.lbl_db_status.setText(f"Fenster für {widget_name} nicht verfügbar !")
            return
        elif self.Main.lnEdit_performer_info.text() == "":
            self.Main.lbl_db_status.setText(f"Kein Namen angebene, ist leer !")
            return
        search_name = self.Main.lnEdit_performer_info.text()        
        dialog = ScrapeActorInfos(search_name, self.Main, parent=self.Main) 
        dialog.setParent(self.Main) 
        dialog.move(pos.x()-150, pos.y() + 20)
        dialog.exec()

    def show_last_logfile(self, pos):
        from utils.web_scapings.theporndb.show_last_log_dialog import ShowLogDialogThePornDB
        self.show_log_dialog = ShowLogDialogThePornDB()          
        self.show_log_dialog.move(pos.x()-150, pos.y() + 20)
        self.show_log_dialog.exec()


    def scrape_babepedia(self, widget_name):
        link = getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip()
        scrape_bapepedia_performer = ScapeBabePediaPerformer(self.Main)
        scrape_bapepedia_performer.load_babepedia_performer_link(link)

    def scrape_the_porn_db(self, widget_name, pos):
        api_link = getattr(self.Main,f"Btn_performer_in_{widget_name}").toolTip()        
        dialog = ScrapeActorInfos(api_link, self.Main, parent=self.Main) 
        dialog.setParent(self.Main)  
        dialog.move(pos.x()-150, pos.y() + 20)
        dialog.exec()

        
