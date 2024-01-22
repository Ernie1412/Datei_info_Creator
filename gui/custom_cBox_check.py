from PyQt6.QtWidgets import QComboBox, QDialog
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt6.QtCore import Qt

import gui.resource_collection_files.labels_rc
from utils.database_settings.database_for_darsteller import DB_Darsteller

class CustomComboBoxCheck(QComboBox):
    def __init__(self, parent):        
        super().__init__(parent)
        self.widget = parent                
        self.setModel(QStandardItemModel(self))
        self.setEditable(True)
        self.view().pressed.connect(self.handleItemPressed) 
        self.lineEdit().setEnabled(False)
        self.currentIndexChanged.connect(self.updatePlaceholderText)

    def addItems(self, type, items, datenbank_darsteller):
        self.datenbank_darsteller = datenbank_darsteller
        self.type=type
        if type == "Nation":
            self.max_labels = 7
        for item in items:
            self.addItem(item)
        self.setCurrentIndex(-1)
        self.setPlaceholderText(f"-- Wähle {self.type} --")

    def handleItemPressed(self, index):        
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)                        
        elif self.type == "Nation":
            if len(self.get_checked_items()) < self.max_labels:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                self.setCurrentText("maximale Anzahl an Labels erreicht")
            self.clear_labels()
            self.set_text_icon_in_labels()
        else:
            item.setCheckState(Qt.CheckState.Checked)       

    def setChecked(self, index):
        item = self.model().item(index)
        item.setCheckState(Qt.CheckState.Checked)
        self.updatePlaceholderText()

    def updatePlaceholderText(self):        
        self.setPlaceholderText("/".join(self.get_checked_items()))
        self.setCurrentIndex(-1)

    def addItem(self, text, checked=False):
        checkState = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        item = QStandardItem(text)
        item.setData(checkState, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)        

    def get_checked_items(self):
        checked_items = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == Qt.CheckState.Checked:
                checked_items.append(item.text())
        return checked_items 
    
    def uncheck_all_items(self):
        for index in range(self.count()):
            item = self.model().item(index)
            item.setCheckState(Qt.CheckState.Unchecked) 
        self.setCurrentIndex(-1)        
        self.setPlaceholderText(f"-- Wähle {self.type} --") 

    def clear_labels(self):
        for label_number in range(1,self.max_labels):
            label = getattr(self.widget, f"lbl_nation_{label_number}")
            label.clear() 

    def set_text_icon_in_labels(self):        
        checked_items = self.get_checked_items()        
        for label_number, text in enumerate(checked_items,1):                       
            label = getattr(self.widget, f"lbl_nation_{label_number}")            
            label.setPixmap(self.get_icon(text))
            label.setToolTip(text)  

    def get_icon(self, text):        
        icon_path = self.datenbank_darsteller.get_nation_kuerzel_from_nation_ger(text)
        return f":/labels/_labels/nations/{icon_path.lower()}.png" 

if __name__ == '__main__':
    CustomComboBoxCheck(QComboBox)