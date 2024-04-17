from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt

class ClickableQLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)        
        self.activated = False  
        
    def mousePressEvent(self, event):  
        if not self.activated: 
            self.setStyleSheet("background-color: #d4ffc4;")
            self.activated = True  
        else:
            self.setStyleSheet("background-color: #FFFDD5;") 
            self.activated = False
    
    def setActivated(self, bolean):
        if bolean:
            self.setStyleSheet("background-color: #d4ffc4;")            
        else:
            self.setStyleSheet("background-color: #FFFDD5;")
        self.activated = bolean