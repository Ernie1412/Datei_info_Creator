from PyQt6.QtWidgets import QPushButton, QMenu, QDialog
from PyQt6 import uic
from PyQt6.QtCore import Qt, pyqtSignal, QVariantAnimation
from PyQt6.QtGui import QPixmap, QColor

import requests
import pyperclip

from config import URL_INPUT_DIALOG_UI

class CustomButton(QPushButton):
    TooltipChanged = pyqtSignal() 

    def __init__(self, parent=None):
        super(CustomButton, self).__init__(parent)        
        self.clicked.connect(self.openDialog)

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        action = self.menu.addAction("Eingabe der URL")
        action.triggered.connect(self.openDialog)
        self.menu.exec(self.mapToGlobal(event.pos()))

    def openDialog(self):        
        self.dialog = QDialog()
        uic.loadUi(URL_INPUT_DIALOG_UI, self.dialog)        
        self.dialog.setStyleSheet("QDialog { border: 2px solid black; }")                
        self.dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint) 
        self.dialog.lnEdit_website_url.setText(self.toolTip()) 
        self.dialog.rejected.connect(self.dialog.close)
        self.dialog.accepted.connect(self.accepted_input_url) 
        self.dialog.Btn_link_copy.clicked.connect(self.copy_clipboard_iafdlink)
        self.dialog.lnEdit_website_url.textChanged.connect(self.check_url_existence)
        self.dialog.exec() 
    
    def accepted_input_url(self):
        self.setToolTip(self.dialog.lnEdit_website_url.text().strip())        
        self.TooltipChanged.emit()
        self.dialog.close()

    def check_url_existence(self):
        url = self.dialog.lnEdit_website_url.text() 
        try:
            response = requests.get(url)            
        except:
            self.dialog.lbl_status.setText("ERROR")
            self.dialog.lblstatus_icon.setPixmap(QPixmap(":/labels/_labels/error.png"))
        else:
            self.dialog.lbl_status.setText(f"{response.status_code}")
            if response.status_code == 200:                
                self.dialog.lblstatus_icon.setPixmap(QPixmap(":/labels/_labels/check.png"))
            else:
                self.dialog.lblstatus_icon.setPixmap(QPixmap(":/labels/_labels/error.png"))
    
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




        