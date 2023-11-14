from PyQt6.QtWidgets import QStatusBar, QMessageBox
from PyQt6.QtCore import QDateTime, QTimer

from pathlib import Path


def StatusBar(self,text,farbe):
    self.statusBar = QStatusBar()
    zeit = QDateTime.currentDateTime().toString('hh:mm:ss')
    self.statusBar.showMessage(f"ℹ️ {zeit}: {text}")         
    self.statusBar.setStyleSheet("border :1px solid ;background-color : "+farbe)
    self.setStatusBar(self.statusBar)   

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
            <img src='{str(Path(__file__).absolute().parent)}/grafics/Error.jpg' alt='Fehler'></img>   
            <p><font-size: 20px><b>{msg_text}</b></p>""") 
        mBox.setWindowTitle("Fehler")     
    elif art=='q':
        mBox.setIcon(QMessageBox.Icon.Question)
        mBox.setText("Fataler Fehler")
        mBox.setInformativeText(f"""</h1><p><font-size: 20px><b>{msg_text}</b></p>""") 
        mBox.setWindowTitle("Was Soll ich machen ?")
        mBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        reply = mBox.exec() 
    else: 
        mBox.setIcon(QMessageBox.Icon.Information)
        mBox.setText("Info !")
        mBox.setInformativeText(f"""<font color='black'>
            <style><background-color='green'>
            <h1 text-align: center></style>                
            <img src='{str(Path(__file__).absolute().parent)}/grafics/Info.jpg' alt='Info'></img>
            <p><font-size: 20px><b>{msg_text}</b></p>""")
        mBox.setWindowTitle("Info")            
        
    return reply
