from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import uic

import sys
from config import PERFORMER_IAFD_UI

class PerformerIAFD(QMainWindow):
    def __init__(self, parent=None):
        super(PerformerIAFD,self).__init__(parent)        
        uic.loadUi(PERFORMER_IAFD_UI,self)






# Abschluss
if __name__ == '__main__':
    app, MainWindow =(QApplication(sys.argv), PerformerIAFD()) 
    MainWindow.show()   
    sys.exit(app.exec())