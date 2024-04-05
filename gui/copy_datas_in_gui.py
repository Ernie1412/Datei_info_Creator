from PyQt6.QtWidgets import QLineEdit, QTextEdit
from PyQt6.QtCore import QVariantAnimation
from PyQt6.QtGui import QColor
import pyperclip

class CopyDatasInGui:
    def __init__(self, MainWindow=None):
        super().__init__()
        self.Main = MainWindow  

    def data18Link_update(self):        
        data18_link=self.Main.lnEdit_DBData18Link.text()
        pyperclip.copy(data18_link)
        self.Main.txtEdit_Clipboard.setPlainText(data18_link) 
        self.widget_animation("lnEdit_DBData18Link")

    def ThePornDBLink_update(self):        
        theporndb_link=self.Main.lnEdit_DBThePornDBLink.text()
        pyperclip.copy(theporndb_link)
        self.Main.txtEdit_Clipboard.setPlainText(theporndb_link) 
        self.widget_animation("lnEdit_DBThePornDBLink") 

    def IAFDLink_update(self):
        iafd_link=self.Main.lnEdit_DBIAFDLink.text()
        pyperclip.copy(iafd_link)
        self.Main.txtEdit_Clipboard.setPlainText(iafd_link)
        self.widget_animation("lnEdit_DBIAFDLink")

    def copy_runtime_set_in_moviedb(self):
        runtime = self.Main.lbl_Dauer.text()
        if runtime:
            self.Main.lnEdit_DBDauer.setText(f"0{runtime}")
            self.widget_animation("lbl_Dauer")

        # kopiere den Text welcher aktiv ist vom Datenbank Tab in die Zwischenablage        
    def copy_text_to_clipboard(self):
        txt: str=None
        widget_name: str=None
        clip_settings = {
            "lnEdit_DBRegie" : "Director: {txt}",
            "lnEdit_DBProDate" : "Comments:\nDate of Production: {txt}",
            "lnEdit_DBRelease" : "Release Date: {txt}",
            "lnEdit_DBDauer" : "Minutes: {txt}",
            "txtEdit_DBMovies" : "Appears In:\n{txt}",
            "txtEdit_DBSynopsis" : "Synopsis:\n{txt}",
        }
        focused_widget = self.Main.grpBox_Daten.focusWidget()  # Das aktuell fokussierte Widget

        if isinstance(focused_widget, QLineEdit):
            text = focused_widget.text()
            widget_name = focused_widget.objectName()
        elif isinstance(focused_widget, QTextEdit):
            text = focused_widget.toPlainText()
            widget_name = focused_widget.objectName()

        if text:                                                   
            if widget_name in clip_settings.keys():                
                pyperclip.copy(clip_settings[widget_name].format(txt=text))
                self.Main.txtEdit_Clipboard.setPlainText(clip_settings[widget_name].format(txt=text))
            else: 
                pyperclip.copy(text)
                self.Main.txtEdit_Clipboard.setPlainText(text)
        else:
            self.Main.txtEdit_Clipboard.setPlainText("❌ kein Feld aktiv !") 

    def copy_iafd_to_clipboard(self)-> None:
        ausgabe:str=""
        for zeile in range(self.Main.tblWdg_DB_performers.rowCount()):
            alias: str=""
            action: str=""
            if self.Main.tblWdg_DB_performers.item(zeile, 1).text()!="":
                alias=" (Credited : "+self.Main.tblWdg_DB_performers.item(zeile, 1).text()+") "
            if self.Main.tblWdg_DB_performers.item(zeile, 2).text()!="":
                action=" <-- "+self.Main.tblWdg_DB_performers.item(zeile, 2).text()
            ausgabe=ausgabe+"\n"+self.Main.tblWdg_DB_performers.item(zeile, 0).text()+alias+action
        iafd=ausgabe[1:]+"\nScene Code: "+self.Main.lnEdit_DBSceneCode.text()+"\nProduction Date: "+self.Main.lnEdit_DBProDate.text()+("\nRegie: "+self.Main.lnEdit_DBRegie.text() if self.Main.lnEdit_DBRegie.text()!="" else "")
        self.Main.txtEdit_Clipboard.setPlainText(iafd)
        pyperclip.copy(iafd) 


    def widget_animation(self, widget, color=None):
        self.animation = QVariantAnimation()
        self.animation.setEndValue(QColor(255, 250, 211)) # rgb(255, 250, 211)
        if color == 'red':            
            self.animation.setStartValue(QColor(255, 100, 100)) # rgb(255, 100, 100)
        else:
            self.animation.setStartValue(QColor(58, 223, 0)) #  rgb(58, 223, 0)
        self.animation.setDuration(1000)
        self.animation.valueChanged.connect(lambda :self.animate(widget))
        self.animation.start()

    def animate(self, widget):
        color = self.animation.currentValue()
        getattr(self.Main,widget).setStyleSheet(f"background-color: {color.name()};")