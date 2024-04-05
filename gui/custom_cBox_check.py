from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer

import gui.resource_collection_files.labels_rc
from utils.database_settings.database_for_darsteller import DB_Darsteller
from gui.get_avaible_labels import GetLabels
class CustomComboBoxCheck(QComboBox):
    update_buttonChanged = pyqtSignal(bool)
    def __init__(self, parent):        
        super().__init__(parent)
        self.widget = parent
        self.setEditable(True)        
        self.setModel(QStandardItemModel(self))        
        self.lineEdit().setReadOnly(True)
        self.closeOnLineEditClick = False
        self.lineEdit().installEventFilter(self)
        self.view().viewport().installEventFilter(self) 
        self.currentIndexChanged.connect(self.updateLineEditField)
    
    def eventFilter(self, widget, event):        
        if widget == self.lineEdit:                        
            if event.type() == QEvent.Type.MouseButtonRelease:
                print("Click")
                if self.closeOnLineEditClick:                    
                    self.closeOnLineEditClick = False
                    self.hidePopup()
                    return True
                else:                    
                    self.closeOnLineEditClick = True
            return True 
        elif widget == self.view().viewport():                        
            if event.type() == QEvent.Type.MouseButtonPress:                
                indx = self.view().indexAt(event.pos())
                item = self.model().item(indx.row())
                self.update_buttonChanged.emit(True)
                if self.type == "Nationen": 
                    if len(self.lineEdit().text().split(", ")) > self.maxlabels-1:
                        self.show_max_labels_warning()
                        return
                newState = Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked
                item.setCheckState(newState)
                self.setCurrentIndex(-1)
                if self.type == "Nationen":
                    self.handleNationType() 
                if self.lineEdit().text() == "":
                    self.show_placeholdertext()
                return True
        return super().eventFilter(widget, event) 

    def handleNationType(self):
        self.clear_labels() 
        self.set_text_icon_in_labels() 

    def show_placeholdertext(self):        
        self.lineEdit().setPlaceholderText(f"-- Wähle {self.type} --")

    def show_max_labels_warning(self):
        self.widget.lbl_maxlabels.setVisible(True)
        self.setVisible(False)
        QTimer.singleShot(1500, lambda: (self.widget.lbl_maxlabels.setVisible(False), self.setVisible(True)))
    
    def addItems(self, main, type, items, datenbank_darsteller=None):
        self.type = type
        self.datenbank_darsteller = datenbank_darsteller        
        if type == "Nationen":
            self.maxlabels = GetLabels().get_available_labels(main, "lbl_performer_nation_")
        for item in items:
            self.addItem(item)  
        self.show_placeholdertext()            

    def setChecked(self, index):
        item = self.model().item(index)
        item.setCheckState(Qt.CheckState.Checked)
        self.updateLineEditField()

    def updateLineEditField(self):         
        if self.lineEdit():
            checked_items = self.get_checked_items()
            if self.type == "Nationen":                
                self.set_text_icon_in_labels()
            if self.type == "Rasse":
                self.lineEdit().setText(self.lineEdit().text().replace(", ","/"))                

    def addItem(self, text, checked=False):
        checkState = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        item = QStandardItem(text)
        item.setData(checkState, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)        

    def get_checked_items(self):
        checked_items = []
        for i in range(self.count()):            
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                checked_items.append(self.model().item(i).text())
        self.lineEdit().setText(", ".join(checked_items))        
        return checked_items 
    
    def uncheck_all_items(self):
        for index in range(self.count()):
            item = self.model().item(index)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.setCurrentIndex(-1)
            self.show_placeholdertext()
            self.setToolTip("")

    def clear_labels(self):
        for label_number in range(self.maxlabels):
            label = getattr(self.widget, f"lbl_nation_{label_number}")
            label.setProperty("nation","")
            label.setStyleSheet("")  
            label.setToolTip("") 

    def set_text_icon_in_labels(self):        
        checked_items = self.get_checked_items()        
        for label_number, text in enumerate(checked_items):                                   
            label = getattr(self.widget, f"lbl_nation_{label_number}")
            label.setProperty("nation",text)
            icon_path = self.get_icon(text)            
            label.setStyleSheet(f"QLabel {{ background-image: url({icon_path});}}")
            label.setToolTip(text)  

    def get_icon(self, text):        
        icon_path = self.datenbank_darsteller.get_nation_kuerzel_from_nation_ger(text)
        return f":/labels/_labels/nations/{icon_path.lower()}.png" 

if __name__ == '__main__':
    CustomComboBoxCheck(QComboBox)