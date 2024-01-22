from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTranslator, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QAbstractItemView, QTableWidgetItem, QApplication, QPushButton, QWidget, QListWidgetItem , \
    QListWidget, QLineEdit, QTextEdit, QComboBox, QTableWidget, QHBoxLayout, QSizePolicy, QToolButton, QSpacerItem, QDialog, QGridLayout, \
    QLabel
from PyQt6.QtGui import QMovie, QPixmap, QKeyEvent, QStandardItem, QStandardItemModel, QColor, QBrush, QIcon
import os
import gui.resource_collection_files.labels_rc

class ComboBoxWidget(QWidget):
    """A single item in listWidget."""
    itemOpSignal = pyqtSignal(QListWidgetItem)

    def __init__(self, text, listwidgetItem):
        super().__init__()
        self.text = text
        self.listwidgetItem = listwidgetItem
        self.initUi()

    def initUi(self):
        self.horizontalLayout = QHBoxLayout(self)
        self.file_btn = QPushButton(QIcon(":/labels/_labels/website.png"), self.text, self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.file_btn.setSizePolicy(sizePolicy)
        qss = '''
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background:transparent;
            }
        '''
        self.file_btn.setStyleSheet(qss)

        self.bt_close = QToolButton(self)
        self.bt_close.setIcon(QIcon(":/labels/_labels/delete_item.png"))
        self.bt_close.setAutoRaise(True)
        self.bt_close.setToolTip("Delete")
        self.bt_close.clicked.connect(lambda: self.itemOpSignal.emit(self.listwidgetItem))

        self.horizontalLayout.addWidget(self.bt_close)
        self.horizontalLayout.addWidget(self.file_btn)
        spacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)


class ListQCombobox(QComboBox):
    def __init__(self, *args):
        super(ListQCombobox, self).__init__(*args)
        self.listw = QListWidget(self)
        self.setModel(self.listw.model())
        self.setView(self.listw)
        self.activated.connect(self.setTopText)
        qss = '''QComboBox QAbstractItemView::item {
                    height: 25px;
                }
                QListView::item:hover {
                    background: #BDD7FD;
                }'''
        self.setStyleSheet(qss)

    def refreshInputs(self, list_inputs):
        self.clear()
        # Loop instantiation to add item
        for num, path in enumerate(list_inputs):
            listwitem = QListWidgetItem(self.listw)
            listwitem.setToolTip(path)
            itemWidget = ComboBoxWidget(os.path.basename(path), listwitem)
            itemWidget.itemOpSignal.connect(self.removeCombo)
            # background color
            if num % 2 == 0:
                listwitem.setBackground(QColor(255, 255, 255))         
            else:
                listwitem.setBackground(QColor(211, 243, 254))
            listwitem.setSizeHint(itemWidget.sizeHint())
            self.listw.addItem(listwitem)
            self.listw.setItemWidget(listwitem, itemWidget)
#@        self.setTopText()
        self.setTopText(listwitem.checkState())                          # +++

    def setTopText(self, index):                                         # + index
        list_text = self.fetchListsText()
        
        if len(list_text) > 1:
            topText = f"{len(list_text)} input files"
        elif len(list_text) == 1:
            topText = os.path.basename(list_text[0])
        else:
            topText = "No input files"
        self.setEditText(topText)
        

        #topText = list_text[index]                                       # +++
        #self.setEditText(topText)                                        # +++

    def refreshBackColors(self):
        for row in range(self.view().count()):
            if row % 2 == 0:
                self.view().item(row).setBackground(QColor(255, 255, 255))
            else:
                self.view().item(row).setBackground(QColor(237, 243, 254))

    def removeCombo(self, listwidgetItem):
        view = self.view()
        index = view.indexFromItem(listwidgetItem)
        view.takeItem(index.row())
        self.refreshBackColors()
#        self.setTopText()

    def fetchListsText(self):
        return [self.view().item(row).toolTip() for row in range(self.view().count())]

    def fetchCurrentText(self):
        if self.view().count():
            return self.view().item(0).toolTip()
        else:
            return ""

    def count(self):
        return self.view().count()


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        list_new_inputs = [r"item 1",  r"item 2", r"item 3", r"item 4"]

        self.gridLayout = QGridLayout(self)
        self.label = QLabel("Combobox: ", self)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)        

        self.comboBox = ListQCombobox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setAcceptDrops(True)
        self.comboBox.setEditable(True)
        self.comboBox.setMinimumContentsLength(15)
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.comboBox.refreshInputs(list_new_inputs)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(app.exec())