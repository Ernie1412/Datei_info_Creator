# Form implementation generated from reading ui file 'e:\Python\Python_WORK\Datei_Info_Creator\gui\uic_imports\_alt\JSON_Maker.ui'
#
# Created by: PyQt6 UI code generator 6.5.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1648, 957)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Btn_Logo = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_Logo.setGeometry(QtCore.QRect(680, 10, 90, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Btn_Logo.setFont(font)
        self.Btn_Logo.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.Btn_Logo.setStyleSheet("background-image: url(:/Logos/grafics/kein_logo.jpg);")
        self.Btn_Logo.setObjectName("Btn_Logo")
        self.lbl_PornSide = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_PornSide.setGeometry(QtCore.QRect(60, 20, 551, 16))
        self.lbl_PornSide.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lbl_PornSide.setText("")
        self.lbl_PornSide.setObjectName("lbl_PornSide")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(30, 0, 611, 51))
        self.groupBox.setObjectName("groupBox")
        self.lblWebside = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblWebside.setGeometry(QtCore.QRect(830, 20, 49, 16))
        self.lblWebside.setText("")
        self.lblWebside.setObjectName("lblWebside")
        self.cBox_Arten = QtWidgets.QComboBox(parent=self.centralwidget)
        self.cBox_Arten.setGeometry(QtCore.QRect(1230, 80, 161, 22))
        self.cBox_Arten.setObjectName("cBox_Arten")
        self.Btn_ADD = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_ADD.setGeometry(QtCore.QRect(1420, 80, 75, 24))
        self.Btn_ADD.setObjectName("Btn_ADD")
        self.Btn_DELETE = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_DELETE.setGeometry(QtCore.QRect(1520, 80, 75, 24))
        self.Btn_DELETE.setObjectName("Btn_DELETE")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(1220, 20, 381, 111))
        self.groupBox_2.setObjectName("groupBox_2")
        self.lnEdit_Inhalt = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lnEdit_Inhalt.setGeometry(QtCore.QRect(10, 20, 361, 22))
        self.lnEdit_Inhalt.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_Inhalt.setObjectName("lnEdit_Inhalt")
        self.Btn_SaveTab = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_SaveTab.setGeometry(QtCore.QRect(780, 10, 90, 40))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Btn_SaveTab.setFont(font)
        self.Btn_SaveTab.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.Btn_SaveTab.setStyleSheet("")
        self.Btn_SaveTab.setObjectName("Btn_SaveTab")
        self.Btn_ButtonMaker = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_ButtonMaker.setGeometry(QtCore.QRect(1420, 150, 90, 40))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Btn_ButtonMaker.setFont(font)
        self.Btn_ButtonMaker.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.Btn_ButtonMaker.setStyleSheet("")
        self.Btn_ButtonMaker.setObjectName("Btn_ButtonMaker")
        self.StartInfos = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.StartInfos.setGeometry(QtCore.QRect(20, 70, 1200, 830))
        self.StartInfos.setObjectName("StartInfos")
        self.tab_ClipInfos = QtWidgets.QWidget()
        self.tab_ClipInfos.setObjectName("tab_ClipInfos")
        self.tblWdg_clip_infos = QtWidgets.QTableWidget(parent=self.tab_ClipInfos)
        self.tblWdg_clip_infos.setGeometry(QtCore.QRect(0, 0, 1200, 820))
        self.tblWdg_clip_infos.setObjectName("tblWdg_clip_infos")
        self.tblWdg_clip_infos.setColumnCount(9)
        self.tblWdg_clip_infos.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_clip_infos.setHorizontalHeaderItem(8, item)
        self.StartInfos.addTab(self.tab_ClipInfos, "")
        self.ttab_tblWdg_csuchinfos = QtWidgets.QWidget()
        self.ttab_tblWdg_csuchinfos.setObjectName("ttab_tblWdg_csuchinfos")
        self.tblWdg_such_infos = QtWidgets.QTableWidget(parent=self.ttab_tblWdg_csuchinfos)
        self.tblWdg_such_infos.setGeometry(QtCore.QRect(0, 0, 1200, 820))
        self.tblWdg_such_infos.setObjectName("tblWdg_such_infos")
        self.tblWdg_such_infos.setColumnCount(9)
        self.tblWdg_such_infos.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_such_infos.setHorizontalHeaderItem(8, item)
        self.StartInfos.addTab(self.ttab_tblWdg_csuchinfos, "")
        self.tab_artistinfos = QtWidgets.QWidget()
        self.tab_artistinfos.setObjectName("tab_artistinfos")
        self.tblWdg_artist_infos = QtWidgets.QTableWidget(parent=self.tab_artistinfos)
        self.tblWdg_artist_infos.setGeometry(QtCore.QRect(0, 0, 1200, 820))
        self.tblWdg_artist_infos.setObjectName("tblWdg_artist_infos")
        self.tblWdg_artist_infos.setColumnCount(9)
        self.tblWdg_artist_infos.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_artist_infos.setHorizontalHeaderItem(8, item)
        self.StartInfos.addTab(self.tab_artistinfos, "")
        self.StartInfos.raise_()
        self.groupBox_2.raise_()
        self.groupBox.raise_()
        self.Btn_Logo.raise_()
        self.lbl_PornSide.raise_()
        self.lblWebside.raise_()
        self.cBox_Arten.raise_()
        self.Btn_ADD.raise_()
        self.Btn_DELETE.raise_()
        self.Btn_SaveTab.raise_()
        self.Btn_ButtonMaker.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1648, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.StartInfos.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Webscraping alle Settings"))
        self.Btn_Logo.setText(_translate("MainWindow", "Laden"))
        self.groupBox.setTitle(_translate("MainWindow", "Porn Side:"))
        self.Btn_ADD.setText(_translate("MainWindow", "ADD"))
        self.Btn_DELETE.setText(_translate("MainWindow", "DELETE"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Tabellen Inhalte Vertikal"))
        self.Btn_SaveTab.setText(_translate("MainWindow", "Speichere\n"
"Tabelle"))
        self.Btn_ButtonMaker.setText(_translate("MainWindow", "Button\n"
"Maker"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "XPath"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Attri"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Clicks"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Weib"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Sleep"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Art"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Single"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Gross"))
        item = self.tblWdg_clip_infos.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Skip"))
        self.StartInfos.setTabText(self.StartInfos.indexOf(self.tab_ClipInfos), _translate("MainWindow", "Clip Infos"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "XPath"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Attri"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Clicks"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Weib"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Sleep"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Art"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Single"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Gross"))
        item = self.tblWdg_such_infos.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Skip"))
        self.StartInfos.setTabText(self.StartInfos.indexOf(self.ttab_tblWdg_csuchinfos), _translate("MainWindow", "Such Infos"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "XPath"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Attri"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Clicks"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Weib"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Sleep"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Art"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Single"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Gross"))
        item = self.tblWdg_artist_infos.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Skip"))
        self.StartInfos.setTabText(self.StartInfos.indexOf(self.tab_artistinfos), _translate("MainWindow", "Darsteller Infos"))