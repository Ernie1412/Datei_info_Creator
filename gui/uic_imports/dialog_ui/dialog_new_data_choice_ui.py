# Form implementation generated from reading ui file 'e:\Python\Python_WORK\Datei_Info_Creator\gui\uic_imports\dialog_ui\dialog_new_data_choice.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(246, 130)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(parent=Dialog)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label = QtWidgets.QLabel(parent=self.splitter)
        self.label.setText("")
        self.label.setObjectName("label")
        self.Btn_close = QtWidgets.QPushButton(parent=self.splitter)
        self.Btn_close.setMinimumSize(QtCore.QSize(20, 20))
        self.Btn_close.setMaximumSize(QtCore.QSize(20, 20))
        self.Btn_close.setAutoFillBackground(False)
        self.Btn_close.setStyleSheet("background-image: url(:/labels/_labels/fenster-schliessen.png);")
        self.Btn_close.setText("")
        self.Btn_close.setFlat(True)
        self.Btn_close.setObjectName("Btn_close")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.gBox_selection_0 = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gBox_selection_0.sizePolicy().hasHeightForWidth())
        self.gBox_selection_0.setSizePolicy(sizePolicy)
        self.gBox_selection_0.setMinimumSize(QtCore.QSize(220, 40))
        self.gBox_selection_0.setMaximumSize(QtCore.QSize(220, 40))
        self.gBox_selection_0.setObjectName("gBox_selection_0")
        self.Btn_selection_0 = QWordWarpButton(parent=self.gBox_selection_0)
        self.Btn_selection_0.setGeometry(QtCore.QRect(-8, 12, 238, 38))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Btn_selection_0.sizePolicy().hasHeightForWidth())
        self.Btn_selection_0.setSizePolicy(sizePolicy)
        self.Btn_selection_0.setMinimumSize(QtCore.QSize(238, 38))
        self.Btn_selection_0.setMaximumSize(QtCore.QSize(238, 38))
        self.Btn_selection_0.setStyleSheet("QPushButton {background-color: #FFFDD5;}\n"
"QLabel {background-color: transparent;}\n"
"QLabel:hover {border: 2px solid rgb(49, 50, 62);}\n"
"QPushButton:focus {border: 2px inset rgb(85, 170, 255);}\n"
"")
        self.Btn_selection_0.setObjectName("Btn_selection_0")
        self.gridLayout.addWidget(self.gBox_selection_0, 1, 0, 1, 1)
        self.gBox_selection_1 = QtWidgets.QGroupBox(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gBox_selection_1.sizePolicy().hasHeightForWidth())
        self.gBox_selection_1.setSizePolicy(sizePolicy)
        self.gBox_selection_1.setMinimumSize(QtCore.QSize(220, 40))
        self.gBox_selection_1.setMaximumSize(QtCore.QSize(220, 40))
        self.gBox_selection_1.setObjectName("gBox_selection_1")
        self.Btn_selection_1 = QWordWarpButton(parent=self.gBox_selection_1)
        self.Btn_selection_1.setGeometry(QtCore.QRect(-8, 12, 238, 38))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Btn_selection_1.sizePolicy().hasHeightForWidth())
        self.Btn_selection_1.setSizePolicy(sizePolicy)
        self.Btn_selection_1.setMinimumSize(QtCore.QSize(238, 38))
        self.Btn_selection_1.setMaximumSize(QtCore.QSize(238, 38))
        self.Btn_selection_1.setStyleSheet("QPushButton {background-color: #FFFDD5;}\n"
"QLabel {background-color: transparent;}\n"
"QLabel:hover {border: 2px solid rgb(49, 50, 62);}\n"
"QPushButton:focus {border: 2px inset rgb(85, 170, 255);}\n"
"")
        self.Btn_selection_1.setObjectName("Btn_selection_1")
        self.gridLayout.addWidget(self.gBox_selection_1, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.Btn_close.setToolTip(_translate("Dialog", "Fenster schliessen"))
        self.gBox_selection_0.setTitle(_translate("Dialog", "Titel"))
        self.Btn_selection_0.setText(_translate("Dialog", "Text123"))
        self.gBox_selection_1.setTitle(_translate("Dialog", "Titel"))
        self.Btn_selection_1.setText(_translate("Dialog", "bla123"))
from gui.custom_wordwrap_button import QWordWarpButton