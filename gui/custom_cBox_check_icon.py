from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize

class CustomComboBoxCheckIcon(QComboBox):
    def __init__(self, parent):        
        super().__init__(parent) 
        self.widgets = parent
                
        self.view().pressed.connect(self.handleItemPressed)        
        self.addItems() 
        self.setEditable(True) 

    def addItems(self):
        for index, (item_text, icon_path) in enumerate(self.widgets.items_dict.items()):             
            icon_path = f":/Buttons/_buttons/{self.widgets.type}/{icon_path}-25.png"
            self.addItem(QIcon(icon_path), item_text)
            self.model().item(index, self.modelColumn()).setCheckState(Qt.CheckState.Unchecked)
    
    def handleItemPressed(self, index):        
        item = self.model().itemFromIndex(index)
        
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
            self.clear_labels()            
        else:
            item_count = len(self.get_checked_items())+1
            if item_count <= self.widgets.max_labels:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                self.setCurrentText(f"maximale Anzahl an Labels erreicht ({item_count}>{self.widgets.max_labels})")
        self.set_text_icon_in_labels()
    
    def get_next_visible_label(self):
        index = 1
        while not hasattr(self.widgets,f"lbl_{self.widgets.type}_{index}").isVisible():             
            index += 1
        return getattr(self.widgets,f"lbl_{self.widgets.type}_{index}")
    
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
        for label_number, (text, icon) in enumerate(checked_items,1):                       
            label = getattr(self.widgets, f"lbl_{self.widgets.type}_{label_number}")            
            label.setPixmap((icon.pixmap(QSize(25, 25))))
            label.setToolTip(text)             

    def clear_labels(self):
        for label_number in range(1,self.widgets.max_labels):
            label = getattr(self.widgets, f"lbl_{self.widgets.type}_{label_number}")
            label.clear()                        
    
if __name__ == '__main__':
    CustomComboBoxCheckIcon(QComboBox)