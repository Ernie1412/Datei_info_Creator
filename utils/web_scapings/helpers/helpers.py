from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from gui.helpers.message_show import MsgBox

class CheckBioWesiteStatus:
    def __init__(self, MainWindow):
            
            super().__init__() 
            self.Main = MainWindow   

    #### ------------ Anzeige ob IAFD, DATA Check negativ,checking, Loading,  OK und error ist ! --------- ####
    #### --------------------------------------------------------------------------------------- ####
    def check_negativ_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setStyleSheet("background-image: url(':/labels/_labels/check_error.png')")
        getattr(self.Main, f"Btn_Linksuche_in_{widget}").setEnabled(False)
        getattr(self.Main,f"lnEdit_DB{widget}Link").blockSignals(True)
        QTimer.singleShot(500, lambda :getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #FF0000'))
        QTimer.singleShot(3000, lambda :getattr(self.Main, f"lnEdit_DB{widget}Link").setText(""))
        QTimer.singleShot(3500, lambda :getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #FFFDD5'))
        getattr(self.Main, f"lnEdit_DB{widget}Link").blockSignals(False) 
    
    def just_checking_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #AAFFFF')        
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setVisible(True)
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setStyleSheet("background-image: url(':/labels/_labels/checking.png')")
        QApplication.processEvents()
    
    def check_OK_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"Btn_Linksuche_in_{widget}").setEnabled(True)
        getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #74DF00')
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setStyleSheet("background-image: url(':/labels/_labels/check.png')")

    def check_error_labelshow(self, widget: str, error="") -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setStyleSheet("background-image: url(':/labels/_labels/timeout.png')")        
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setToolTip(error)
        getattr(self.Main, f"Btn_Linksuche_in_{widget}").setEnabled(False) 
        getattr(self.Main, f"lnEdit_DB{widget}Link").blockSignals(True)           
        getattr(self.Main, f"lnEdit_DB{widget}Link").setText("")
        getattr(self.Main, f"lnEdit_DB{widget}Link").setStyleSheet('background-color: #FFFDD5')
        getattr(self.Main, f"lnEdit_DB{widget}Link").blockSignals(False)

    def check_loading_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setStyleSheet("background-image: url(':/labels/_labels/loading_page.png')") 
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setToolTip("") 
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").repaint()

    def check_loaded_labelshow(self, widget: str) -> None:
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setStyleSheet("background-image: url(':/labels/_labels/done.png')") 

    def fehler_ausgabe_checkweb(self, error, widget: str, msgbox_show: bool=False) -> None:
        if msgbox_show:
            MsgBox(self.Main, error,"w")        
        code = error.code if hasattr(error, 'code') else "N/A"            
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setStyleSheet("background-image: url(':/labels/_labels/error.png')")            
        getattr(self.Main, f"lbl_checkWeb_{widget}URL").setToolTip(str(error)) 