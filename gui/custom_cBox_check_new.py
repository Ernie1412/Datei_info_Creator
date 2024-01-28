from typing import Iterable
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal, QEvent

import gui.resource_collection_files.labels_rc
from utils.database_settings.database_for_darsteller import DB_Darsteller
from gui.get_avaible_labels import GetLabels
class CustomComboBoxCheckNew(QComboBox):
    update_buttonChanged = pyqtSignal(bool)
    def __init__(self, parent):        
        super().__init__(parent)  
        self.setEditable(True) 
        self.lineEdit().setReadOnly(True)
        self.closeOnLineEditClick = False
        self.lineEdit().installEventFilter(self)
        self.view().viewport().installEventFilter(self)
        self.model().dataChanged.connect(self.updateLineEditField) 
        self.setCurrentIndex(-1)
        self.setPlaceholderText("-- Wähle Nationen --")
      
    def eventFilter(self, widget, event):
        if widget == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    
                    self.closeOnLineEditClick = False
                else:                    
                    self.closeOnLineEditClick = True
                return True            
        elif widget == self.view().viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                indx = self.view().indexAt(event.pos())
                item = self.model().item(indx.row())
                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                return True              
        return super().eventFilter(widget, event)     
    
    def hidePopup(self) -> None:
        super().hidePopup()
        self.startTimer(100)
    
    def addItems(self, main,  type, items, itemList=None) -> None:
        if type == "Nation":
            self.maxlabels = GetLabels().get_available_labels(main, "lbl_performer_nation_")
        for indx, item in enumerate(items):
            try:
                data = itemList[indx]
            except (TypeError, IndexError):
                data = None 
            self.addItem(item, data)
    
    def addItem(self, text, userData=None):        
        item = QStandardItem(text)
        if not userData is None:
            item.setData(userData)

        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def updateLineEditField(self):
        text_container = []
        for i in range(self.model().rowCount()):            
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                text_container.append(self.model().item(i).text())
        self.lineEdit().setText(", ".join(text_container))
    