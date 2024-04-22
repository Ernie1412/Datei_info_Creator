from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

class QWordWarpButton(QWidget):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # QPushButton initialisieren
        self.button = QPushButton(self)  
        self.button.clicked.connect(self.clicked.emit)      
        
        # QLabel initialisieren
        self.label = QLabel(self.button)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        
        # QPushButton Methoden umleiten
        self.setText = self.label.setText
        self.text = self.label.text  
        self.label.setFixedSize = self.button.setFixedSize
        self.label.setMinimumSize = self.button.setMinimumSize
        self.label.setMaximumSize = self.button.setMaximumSize
        self.setFont = self.button.setFont

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Passen Sie die Größe des Labels an, um den Button abzudecken, abzüglich des Randes
        padding = 10  # Rand von 10 Pixeln
        self.label.setGeometry(0, -10+padding, self.width()-2*padding, self.height()-2*padding)

if __name__ == '__main__':
    QWordWarpButton(QWidget)