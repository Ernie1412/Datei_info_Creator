from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTranslator, pyqtSlot
from PyQt6.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem, QApplication, QPushButton, QWidget, QListWidgetItem , \
    QListWidget, QLineEdit, QTextEdit, QComboBox
from PyQt6.QtGui import QMovie, QPixmap, QKeyEvent, QStandardItem, QStandardItemModel, QColor, QBrush

import sys
from pathlib import Path


class WordWrap(QDialog):    
    def __init__(self, parent=None):
        super().__init__(parent)        
        uic.loadUi(Path(__file__).absolute().parent / "gui/uic_imports/Btn_wordwrap.ui",self)
        
        self.pushButton.setText("In an effort to provide with you with choices, the IAFD has partnered with leading online retailers to provide you with purchase options. If you see an item that does not belong to this movie, or would like to suggest a retailer we should partner with, please use the 'Submit Corrections' button above to let us know.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = WordWrap()
    dialog.exec()

