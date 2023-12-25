from PyQt6.QtWidgets import QStatusBar, QMessageBox
from PyQt6.QtCore import QDateTime, QTimer

from pathlib import Path
from config import PROJECT_PATH


def StatusBar(self,text,farbe):
    self.statusBar = QStatusBar()
    zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
    self.statusBar.showMessage(f"ℹ️ {zeit}: {text}")         
    self.statusBar.setStyleSheet("border :1px solid ;background-color : "+farbe)
    self.setStatusBar(self.statusBar) 
    QTimer.singleShot(4500, lambda :self.statusBar.setStyleSheet("background-color : #fffdb7"))  

def status_fehler_ausgabe(self,message):
    StatusBar(self, message,"#F78181")                       
    QTimer.singleShot(500, lambda :StatusBar(self, message,"#fffdb7"))
    QTimer.singleShot(1000, lambda :StatusBar(self, message,"#F78181"))
    QTimer.singleShot(1500, lambda :StatusBar(self, message,"#fffdb7"))

def MsgBox(self, msg_text: str, art: str) -> QMessageBox:
    mBox: QMessageBox = QMessageBox()
    reply: str=None
    
    if art=='w': 
        mBox.setIcon(QMessageBox.Icon.Warning)
        mBox.setText("Fehler !") 
        mBox.setInformativeText(f"""<font color='black'><style><background-color='yellow'><h1 text-align: center></style>
            <img src='{PROJECT_PATH}/grafics/error_.jpg' alt='Fehler'></img><p><font-size: 20px><b>{msg_text}</p></h1>""") 
        mBox.setWindowTitle("Fehler") 
        mBox.exec()
    elif art=='q':
        mBox.setIcon(QMessageBox.Icon.Question)
        mBox.setText("Fataler Fehler")
        mBox.setInformativeText(f"""<p><font-size: 20px><b>{msg_text}</p>""") 
        mBox.setWindowTitle("Was Soll ich machen ?")
        mBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)        
        reply = mBox.exec() 
    else: 
        mBox.setIcon(QMessageBox.Icon.Information)
        mBox.setText("Info !")
        mBox.setInformativeText(f"""<font color='black'><style><background-color='green'><h1 text-align: center></style>                
            <img src='{PROJECT_PATH}/grafics/Info.jpg' alt='Info'></img><p><font-size: 20px><b>{msg_text}</p></h1>""")
        mBox.setWindowTitle("Info")            
        mBox.exec()
    return reply

def blink_label(self, label_widget, farbe):
    getattr(self, label_widget).setStyleSheet(f'background-color: {farbe}')
    QTimer.singleShot(1000, lambda :getattr(self, label_widget).setStyleSheet('background-color: '))
    QTimer.singleShot(2000, lambda :getattr(self, label_widget).setStyleSheet(f'background-color: {farbe}'))
    QTimer.singleShot(3000, lambda :getattr(self, label_widget).setStyleSheet('background-color: '))

