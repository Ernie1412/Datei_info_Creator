from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout

class QWordWarpButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # QPushButton initialisieren
        self.button = QPushButton(self)        
        
        # QLabel initialisieren
        self.label = QLabel(self.button)
        self.label.setWordWrap(True)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        
        # QPushButton Methoden umleiten
        self.setText = self.label.setText
        self.text = self.label.text
        self.setFixedSize = self.button.setFixedSize
        self.setMinimumSize = self.button.setMinimumSize
        self.setMaximumSize = self.button.setMaximumSize
        self.setFont = self.button.setFont