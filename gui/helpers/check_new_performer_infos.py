from PyQt6.QtWidgets import QWidget

from gui.dialog_performer_mask_selection import PerformMaskSelection

class CheckNewPerformerInfos():
    def __init__(self, MainWindow):
        super().__init__()
        self.Main = MainWindow

    def check_selections_count(self, widget_type, value): 
        if not value:
            return
        
        widget_name, current_text, set_method_name = self.get_widget_and_current(widget_type)
        if current_text == value:
            return
        
        if widget_type in ['height','weight']:
            current_min, current_max  = (int(current_text)-4, int(current_text)+4)  if current_text else (0,0)
            if int(value) in range(current_min, current_max+1):
                return
            
        if not current_text:            
            method = getattr(widget_name, set_method_name)
            method(value)
        else:    
            self.update_selection_button(widget_type, value, widget_name)
        
    def update_selection_button(self, widget_type, value, widget_name):
        button = getattr(self.Main,f"Btn_{widget_type}_selection")                              
        button.setVisible(True)
        counter = int(button.text()) + 1 if button.text() else "1"
        button.setText(str(counter)) 
        try:
            button.clicked.disconnect()
        except TypeError:
            pass 
        button.clicked.connect(lambda _, widget_name=widget_name: self.connect_button_clicked(widget_name))

    def get_widget_and_current(self, widget_type):
        if widget_type in ["piercing", "tattoo"]:
            widget_name = getattr(self.Main, f"txtEdit_performer_{widget_type}")
            widget_text = widget_name.toPlainText()
            set_method_name = "setPlainText"
        elif widget_type in ["eye", "rasse"]:
            widget_name = getattr(self.Main, f"cBox_performer_{widget_type}")
            widget_text = widget_name.currentText()
            set_method_name = "setCurrentText"
        else:
            widget_name = getattr(self.Main, f"lnEdit_performer_{widget_type}")
            widget_text = widget_name.text()
            set_method_name = "setText"
        return widget_name, widget_text, set_method_name

    def connect_button_clicked(self, widget_name):
        widget_name = widget_name.objectName()
        mask_selection_dialog = PerformMaskSelection(self.Main, widget_name)
        mask_selection_dialog.exec()