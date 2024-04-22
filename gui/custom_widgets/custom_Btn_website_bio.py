from PyQt6.QtWidgets import QPushButton, QMenu, QDialog
from PyQt6 import uic
from PyQt6.QtCore import Qt, pyqtSignal, QVariantAnimation, QSize
from PyQt6.QtGui import QPixmap, QColor

import requests
import pyperclip

from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper
from gui.clearing_widgets import ClearingWidget

from config import URL_INPUT_FOR_BIOSITES_DIALOG_UI

class CustomButton(QPushButton):
    tooltipChanged = pyqtSignal()     
    def __init__(self, parent=None):
        super(CustomButton, self).__init__(parent)
        self.Main = parent
        self.clicked.connect(self.openDialog)
        self.button_name = None

    def set_websitebio_logo(self, parent):
        sender = parent.sender()
        if sender:
            self.button_name = sender.objectName().replace("Btn_performer_in_","")
            websitebio_logo = sender.icon()
            icon_pixmap = websitebio_logo.pixmap(websitebio_logo.actualSize(QSize(50, 25)))
            getattr(self.dialog,"lbl_bio_logo").setPixmap(icon_pixmap)

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        action = self.menu.addAction("Eingabe der URL")
        action.triggered.connect(self.openDialog)
        self.menu.exec(self.mapToGlobal(event.pos()))

    def openDialog(self):        
        self.dialog = QDialog()
        uic.loadUi(URL_INPUT_FOR_BIOSITES_DIALOG_UI, self.dialog)  
        self.dialog.chkBox_get_autom_iafd.setVisible(False) 
        self.dialog.chkBox_iafd_enabled.setVisible(False)      
        self.dialog.setStyleSheet("QDialog { border: 2px solid black; }")                
        self.dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint) 
        self.dialog.lnEdit_website_url.setText(self.toolTip()) 
        self.dialog.Btn_close.clicked.connect(self.dialog.close)
        self.dialog.Btn_OK.clicked.connect(self.accepted_input_url) 
        self.dialog.Btn_link_copy.clicked.connect(self.copy_clipboard_iafdlink)
        self.dialog.lnEdit_website_url.textChanged.connect(self.check_url_existence)
        self.dialog.chkBox_iafd_enabled.stateChanged.connect(self.toggle_iafd_performer_state)
        self.set_websitebio_logo(self.Main)
        if self.dialog.lnEdit_website_url.text().startswith("https://www.iafd.com/person.rme/perfid="):
            self.dialog.chkBox_get_autom_iafd.setVisible(True)
            self.dialog.chkBox_iafd_enabled.setVisible(True)
        self.dialog.exec() 
    
    def accepted_input_url(self):
        self.setToolTip(self.dialog.lnEdit_website_url.text().strip())        
        self.tooltipChanged.emit()
        self.dialog.close()

    def check_url_existence(self):
        response = None
        link = self.dialog.lnEdit_website_url.text().strip() 
        if self.button_name == "ThePornDB":
            response = self.check_url_tpdb(link)
        if response == None:
            return
                    
        self.dialog.lbl_status.setText(f"{response}")
        if response == 200:  
            self.dialog.lblstatus_icon.setPixmap(QPixmap(":/labels/_labels/check.png"))
        else:
            self.dialog.lblstatus_icon.setPixmap(QPixmap(":/labels/_labels/error.png"))
    
    def check_url_tpdb(self, link):        
        if not link.startswith('https://api.theporndb.net/performers/'):                       
            self.dialog.lbl_status.setText("ERROR")
            self.dialog.lblstatus_icon.setPixmap(QPixmap(":/labels/_labels/error.png"))
            self.dialog.lnEdit_website_url.setText("")
            return None
        return TPDB_Scraper.check_tpdb_data(link)

    def copy_clipboard_iafdlink(self):
        if self.dialog.lnEdit_website_url.text():
            pyperclip.copy(self.dialog.lnEdit_website_url.text())
            self.widget_animation("lnEdit_website_url")

    def widget_animation(self, widget):
        self.animation = QVariantAnimation()
        self.animation.setEndValue(QColor(255, 250, 211)) # rgb(255, 250, 211)
        self.animation.setStartValue(QColor(58, 223, 0)) #  rgb(58, 223, 0)
        self.animation.setDuration(1000)
        self.animation.valueChanged.connect(lambda :self.animate(widget))
        self.animation.start()
        
    def animate(self, widget):
        color = self.animation.currentValue()
        getattr(self.dialog, widget).setStyleSheet(f"background-color: {color.name()};")

    def toggle_iafd_performer_state(self, is_checked):
        clearing = ClearingWidget(self.Main)        
        is_change=False
        # Überprüfen, ob der veränderungen ist und die Farbe entsprechend setzen
        if self.Main.lnEdit_DBWebSite_artistLink_old != self.Main.lnEdit_DBWebSite_artistLink.text() and self.Main.lnEdit_DBWebSite_artistLink.text() != "N/A":
            is_change=True
            self.Main.lnEdit_DBWebSite_artistLink_old = self.Main.lnEdit_DBWebSite_artistLink.text()
            self.Main.lnEdit_IAFD_artistAlias_old = self.Main.lnEdit_IAFD_artistAlias.text()
        self.Main.set_default_color("lnEdit_DBWebSite_artistLink")
        color_hex = '#FFFD00' if is_change or not is_checked else '#FFFDD5' 

        self.Main.set_color_stylesheet("lnEdit_DBWebSite_artistLink", color_hex=color_hex)
        self.Main.set_color_stylesheet("lnEdit_IAFD_artistAlias", color_hex=color_hex)  

        self.Main.Btn_performer_in_IAFD.setToolTip(self.Main.lnEdit_DBWebSite_artistLink_old if is_checked else "N/A")
        self.Main.lnEdit_IAFD_artistAlias.setText(self.Main.lnEdit_IAFD_artistAlias_old if is_checked else "")
        
        clearing.set_website_bio_enabled(['IAFD'], is_checked)
        self.Main.lnEdit_IAFD_artistAlias.setEnabled(is_checked)




        