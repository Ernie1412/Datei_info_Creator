import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QDialog, QGroupBox
from PyQt6.QtCore import Qt, QRect
from functools import partial

class Dlg_Daten_Auswahl(QDialog):
    def __init__(self, MainWindow):
        super().__init__()
        self.Main = MainWindow
        button_maske: str = self.Main.sender().whatsThis()
        self.setWindowTitle(f"Auswahl für: {button_maske}")
        self.resize(840, 700)
        self.setModal(True)
        self.main_layout = QVBoxLayout(self)              
        
        # Dynamisch Buttons hinzufügen
        sources, daten = self.Main.datenbank_load_maske(button_maske)

        button_index: int=0
        for grpBox_source, data_text  in zip(sources, daten):
            self.qpushbutton_wordwrap(button_index, data_text, grpBox_source, self.main_layout)
            button_index += 1

        # Zurück-Button in der unteren Ecke
        back_button = QPushButton('Zurück', self)
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(back_button)
        layout.setAlignment(back_button, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)  # Unten rechts
        self.main_layout.addLayout(layout)  # Unten rechts

        back_button.clicked.connect(self.reject)        

        for button_index, data_text in enumerate(daten):
            button_widget = self.findChild(QPushButton, f'Btn_daten_{button_index}')
            if button_widget:
                button_widget.clicked.connect(partial(self.dialog_auswahl, button_maske, button_index, data_text))  
        

    def qpushbutton_wordwrap(self, index, text, grpBox_text, parent_layout):        
        #widget_container = QWidget()  # Container-Widget für QPushButton und QLabel
        #widget_layout = QHBoxLayout(widget_container)
        group_box = QGroupBox(grpBox_text, self)
        group_box.setStyleSheet("QGroupBox { background-color: rgb(211, 211, 211);\nborder-radius: 5px;}")
        group_layout = QVBoxLayout(group_box)
        btn = QPushButton(group_box)
        btn.setObjectName(f"Btn_daten_{index}")
        btn.setGeometry(QRect(20, 30, 780, 120))        
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(255, 253, 213);
                border: 1px solid transparent;
                padding: 5px 10px;
            }
            QPushButton:focus {
                border: 2px inset rgb(85, 170, 255);
            }              
            QPushButton:hover {
                border: 2px solid rgb(49, 50, 62);
            }   """)
        
        label = QLabel(text, btn)    
        label.setWordWrap(True)
        
        button_layout = QHBoxLayout(btn)    
        button_layout.addWidget(label)        
        group_layout.setContentsMargins(10, 0, 10, 0)
        parent_layout.addWidget(group_box)
        

    def dialog_auswahl(self,button_maske: str, index: int, daten: str) -> None:
        daten: str = daten.replace("\n", "")        
        if button_maske in ["Movies", "Tags", "Synopsis"]:
            getattr(self.Main, f"txtEdit_DB{button_maske}").setPlainText(daten)
        else:
            getattr(self.Main, f"lnEdit_DB{button_maske}").setText(daten)
        self.reject()

def main():
    app = QApplication(sys.argv)
    dialog = Dlg_Daten_Auswahl()
    dialog.exec()

if __name__ == '__main__':
    main()









