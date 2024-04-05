from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer

from gui.get_avaible_labels import GetLabels

class CustomComboBoxCheckIcon(QComboBox):
    def __init__(self, parent):        
        super().__init__(parent) 
        self.widgets = parent 
        self.setEditable(True)        
        self.setModel(QStandardItemModel(self))        
        self.lineEdit().setReadOnly(True)
        self.closeOnLineEditClick = False
        self.lineEdit().installEventFilter(self)
        self.view().viewport().installEventFilter(self)        

    def eventFilter(self, widget, event):        
        if widget == self.lineEdit:                        
            if event.type() == QEvent.Type.MouseButtonRelease:                
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
                if len(self.get_checked_items()) > self.widgets.maxlabels-1:
                    self.show_max_labels_warning()
                    return
                newState = Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked
                item.setCheckState(newState)
                self.set_text_icon_in_labels()  
                return True
        return super().eventFilter(widget, event)

    def addItems(self, main, dict_items):
        for index, (item_text, icon_path) in enumerate(dict_items.items()):             
            icon_path = f":/Buttons/_buttons/socialmedia/{icon_path}-25.png"
            self.addItem(item_text, QIcon(icon_path), checked=False)
        self.setCurrentIndex(-1)
        self.lineEdit().setPlaceholderText("Auswahl an Sozial Media Links")
    
    def addItem(self, text, icon=None, checked=False):
        checkState = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        item = QStandardItem()
        if icon is not None:
            item.setIcon(QIcon(icon))        
        item.setText(text)
        item.setCheckable(True)  # Damit das Element ein Kontrollkästchen hat
        item.setCheckState(checkState)
        self.model().appendRow(item)

    def get_next_visible_label(self):
        index = 0
        while not hasattr(self.widgets,f"lbl_socialmedia_{index}").isVisible():             
            index += 1
        return getattr(self.widgets,f"lbl_socialmedia_{index}")
    
    def show_max_labels_warning(self):
        self.widgets.lbl_maxlabels.setVisible(True)
        self.setVisible(False)
        QTimer.singleShot(1500, lambda: (self.widgets.lbl_maxlabels.setVisible(False), self.setVisible(True)))
        
    def get_checked_items(self):
        checked_items = []
        for index in range(self.count()):
            model_index = self.model().index(index, self.modelColumn())
            item = self.model().itemFromIndex(model_index)
            if item.checkState() == Qt.CheckState.Checked: 
                checked_items.append((item.text(),self.itemIcon(model_index.row())))
        return checked_items 
    
    def set_text_icon_in_labels(self):        
        checked_items = self.get_checked_items()        
        for label_number, (text, icon) in enumerate(checked_items):                       
            label = getattr(self.widgets, f"lbl_socialmedia_{label_number}")            
            label.setPixmap((icon.pixmap(QSize(25, 25))))
            label.setToolTip(text)
            label.setProperty("socialmedia",text)             

    def clear_labels(self):
        for label_number in range(self.widgets.maxlabels):
            label = getattr(self.widgets, f"lbl_socialmedia_{label_number}")
            label.clear()                        
    
if __name__ == '__main__':
    CustomComboBoxCheckIcon(QComboBox)