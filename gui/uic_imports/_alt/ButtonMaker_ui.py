# Form implementation generated from reading ui file 'e:\Python\Python_WORK\Datei_Info_Creator\gui\uic_imports\_alt\ButtonMaker.ui'
#
# Created by: PyQt6 UI code generator 6.5.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ButtonMaker(object):
    def setupUi(self, ButtonMaker):
        ButtonMaker.setObjectName("ButtonMaker")
        ButtonMaker.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=ButtonMaker)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(110, 80, 41, 16))
        self.label.setObjectName("label")
        self.lbl_Ordner = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_Ordner.setGeometry(QtCore.QRect(150, 80, 521, 16))
        self.lbl_Ordner.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lbl_Ordner.setText("")
        self.lbl_Ordner.setObjectName("lbl_Ordner")
        self.lbl_Logo = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_Logo.setGeometry(QtCore.QRect(50, 160, 291, 151))
        self.lbl_Logo.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lbl_Logo.setText("")
        self.lbl_Logo.setScaledContents(True)
        self.lbl_Logo.setObjectName("lbl_Logo")
        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(50, 130, 47, 13))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(420, 190, 47, 13))
        self.label_5.setObjectName("label_5")
        self.lbl_160x60 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_160x60.setGeometry(QtCore.QRect(420, 220, 160, 90))
        self.lbl_160x60.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lbl_160x60.setText("")
        self.lbl_160x60.setObjectName("lbl_160x60")
        self.label_7 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(650, 240, 47, 13))
        self.label_7.setObjectName("label_7")
        self.lbl_90x40 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_90x40.setGeometry(QtCore.QRect(650, 270, 90, 40))
        self.lbl_90x40.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lbl_90x40.setText("")
        self.lbl_90x40.setObjectName("lbl_90x40")
        self.Btn_Laden = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_Laden.setGeometry(QtCore.QRect(610, 120, 121, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.Btn_Laden.setFont(font)
        self.Btn_Laden.setStyleSheet("border-style: outset;\n"
"background-color: rgb(205, 205, 205);\n"
"border-width: 2px;\n"
"border-radius: 10px;\n"
"border-color: beige;\n"
"font: 20pt \"MS Shell Dlg 2\";")
        self.Btn_Laden.setObjectName("Btn_Laden")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(100, 50, 41, 16))
        self.label_2.setObjectName("label_2")
        self.lbl_Filename = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_Filename.setGeometry(QtCore.QRect(150, 50, 521, 16))
        self.lbl_Filename.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lbl_Filename.setText("")
        self.lbl_Filename.setObjectName("lbl_Filename")
        ButtonMaker.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=ButtonMaker)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        ButtonMaker.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=ButtonMaker)
        self.statusbar.setObjectName("statusbar")
        ButtonMaker.setStatusBar(self.statusbar)

        self.retranslateUi(ButtonMaker)
        QtCore.QMetaObject.connectSlotsByName(ButtonMaker)

    def retranslateUi(self, ButtonMaker):
        _translate = QtCore.QCoreApplication.translate
        ButtonMaker.setWindowTitle(_translate("ButtonMaker", "Button Maker 1.0"))
        self.label.setText(_translate("ButtonMaker", "Ordner"))
        self.label_4.setText(_translate("ButtonMaker", "Logo"))
        self.label_5.setText(_translate("ButtonMaker", "160x60"))
        self.label_7.setText(_translate("ButtonMaker", "90x40"))
        self.Btn_Laden.setText(_translate("ButtonMaker", "Laden"))
        self.label_2.setText(_translate("ButtonMaker", "Filename"))
