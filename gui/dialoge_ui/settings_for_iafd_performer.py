from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt



from config import SETTINGS_FOR_IAFD_PERFORMER_UI

class SettingsForIAFDPerformer(QDialog):

    def __init__(self, parent): # von wo es kommt 
        super(SettingsForIAFDPerformer,self).__init__(parent) 
        self.Main = parent   
        uic.loadUi(SETTINGS_FOR_IAFD_PERFORMER_UI, self) 
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  
        self.Btn_OK.clicked.connect(self.accepted)


if __name__ == '__main__':
    SettingsForIAFDPerformer(QDialog)