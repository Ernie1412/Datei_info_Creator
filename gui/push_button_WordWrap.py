from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QRect, QSize

from gui.uic_imports.Btn_wordwrap_ui import Ui_Dialog

class CustomButtonWordWrap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.btn = QPushButton(parent)
        #self.ui.btn.setGeometry(QRect(220, 260, 271, 121))
        #self.ui.btn.setMinimumSize(QSize(200, 50))
        self.ui.label = QLabel("", self.btn)
        self.ui.label.setWordWrap(True)

        layout = QHBoxLayout(self.ui.btn)
        layout.addWidget(self.ui.label, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    # def setText(self, text):
    #     self.label.setText(text)