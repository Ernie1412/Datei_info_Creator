# Form implementation generated from reading ui file 'e:\Python\Python_WORK\Datei_Info_Creator\gui\uic_imports\_alt\websides - Kopie.ui'
#
# Created by: PyQt6 UI code generator 6.5.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Haupt_Fenster(object):
    def setupUi(self, Haupt_Fenster):
        Haupt_Fenster.setObjectName("Haupt_Fenster")
        Haupt_Fenster.resize(1910, 1016)
        self.centralwidget = QtWidgets.QWidget(parent=Haupt_Fenster)
        self.centralwidget.setObjectName("centralwidget")
        self.Btn_Suchen = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_Suchen.setEnabled(True)
        self.Btn_Suchen.setGeometry(QtCore.QRect(410, 20, 121, 61))
        self.Btn_Suchen.setStyleSheet("QPushButton { \n"
"    color: rgb(0, 0, 127);\n"
"    selection-background-color: rgb(255, 85, 0);\n"
"    background-color: rgb(198, 178, 255);\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    font: 22pt \"MS Shell Dlg 2\";\n"
"    border-radius: 10px;\n"
"    border-color: beige;\n"
"}                   \n"
"QPushButton:enabled{\n"
"    background-color: rgb(198, 178, 255);\n"
"}                           \n"
"QPushButton:pressed{ \n"
"    background: red;\n"
"}                            \n"
"QPushButton:disabled{                             \n"
"    background-color: gray;                \n"
"}\n"
"QPushButton:hover{\n"
"    background-color: rgb(255, 85, 255);\n"
"}         ")
        self.Btn_Suchen.setObjectName("Btn_Suchen")
        self.Btn_VideoData = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_VideoData.setEnabled(True)
        self.Btn_VideoData.setGeometry(QtCore.QRect(280, 20, 121, 61))
        self.Btn_VideoData.setStyleSheet("QPushButton { \n"
"    font: 11pt \"MS Shell Dlg 2\";\n"
"    color: rgb(0, 0, 127);\n"
"    selection-background-color: rgb(255, 85, 0);\n"
"    background-color: rgb(198, 178, 255);\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    font: 75 12pt \"MS Shell Dlg 2\";\n"
"    border-radius: 10px;\n"
"    border-color: beige;\n"
"}                   \n"
"QPushButton:enabled{\n"
"    background-color: rgb(198, 178, 255);\n"
"}                           \n"
"QPushButton:pressed{ \n"
"    background: red;\n"
"}                            \n"
"QPushButton:disabled{                             \n"
"    background-color: gray;                \n"
"}\n"
"QPushButton:hover{\n"
"    background-color: rgb(255, 85, 255);\n"
"}         ")
        self.Btn_VideoData.setCheckable(True)
        self.Btn_VideoData.setObjectName("Btn_VideoData")
        self.Btn_IAFDLinken = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_IAFDLinken.setGeometry(QtCore.QRect(540, 20, 131, 61))
        self.Btn_IAFDLinken.setStyleSheet("QPushButton { \n"
"    color: rgb(0, 0, 127);\n"
"    selection-background-color: rgb(255, 85, 0);\n"
"    background-color: rgb(198, 178, 255);\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    font: 16pt \"MS Shell Dlg 2\";\n"
"    border-radius: 10px;\n"
"    border-color: beige;\n"
"}                   \n"
"QPushButton:enabled{\n"
"    background-color: rgb(198, 178, 255);\n"
"}                           \n"
"QPushButton:pressed{ \n"
"    background: red;\n"
"}                            \n"
"QPushButton:disabled{                             \n"
"    background-color: gray;                \n"
"}\n"
"QPushButton:hover{\n"
"    background-color: rgb(255, 85, 255);\n"
"}         ")
        self.Btn_IAFDLinken.setObjectName("Btn_IAFDLinken")
        self.Btn_VideoDB = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_VideoDB.setEnabled(True)
        self.Btn_VideoDB.setGeometry(QtCore.QRect(20, 20, 121, 61))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.Btn_VideoDB.setFont(font)
        self.Btn_VideoDB.setStyleSheet("QPushButton { \n"
"    color: rgb(0, 0, 127);\n"
"    selection-background-color: rgb(255, 85, 0);\n"
"    background-color: rgb(198, 178, 255);\n"
"   \n"
"    border-image: url(:/Video_DBauffuellen/database_add.png);\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    font: 14pt \"MS Shell Dlg 2\";\n"
"    border-radius: 10px;\n"
"    border-color: beige;\n"
"}                   \n"
"\n"
"QPushButton:enabled{\n"
"    background-color: rgb(198, 178, 255);\n"
"}                           \n"
"QPushButton:pressed{ \n"
"    background: red;\n"
"}                            \n"
"QPushButton:disabled{                             \n"
"    background-color: gray;                \n"
"}\n"
"QPushButton:hover{\n"
"    background-color: rgb(255, 85, 255);\n"
"}         ")
        icon = QtGui.QIcon.fromTheme("ui\\graphics\\database_add.png")
        self.Btn_VideoDB.setIcon(icon)
        self.Btn_VideoDB.setObjectName("Btn_VideoDB")
        self.lbl_Titel = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_Titel.setGeometry(QtCore.QRect(30, 100, 31, 16))
        self.lbl_Titel.setObjectName("lbl_Titel")
        self.lnEdit_Titel = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_Titel.setGeometry(QtCore.QRect(60, 100, 481, 20))
        self.lnEdit_Titel.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_Titel.setText("")
        self.lnEdit_Titel.setObjectName("lnEdit_Titel")
        self.lnEdit_Jahr = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_Jahr.setGeometry(QtCore.QRect(60, 130, 71, 20))
        self.lnEdit_Jahr.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_Jahr.setText("")
        self.lnEdit_Jahr.setObjectName("lnEdit_Jahr")
        self.lblJahr = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblJahr.setGeometry(QtCore.QRect(30, 130, 31, 16))
        self.lblJahr.setObjectName("lblJahr")
        self.lblAFDLink = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblAFDLink.setGeometry(QtCore.QRect(30, 160, 791, 20))
        self.lblAFDLink.setStyleSheet("background-color: rgb(255, 250, 211);")
        self.lblAFDLink.setText("")
        self.lblAFDLink.setObjectName("lblAFDLink")
        self.Btn_CopyLink = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_CopyLink.setGeometry(QtCore.QRect(830, 153, 81, 31))
        self.Btn_CopyLink.setStyleSheet("QPushButton { \n"
"    color: rgb(0, 0, 127);\n"
"    selection-background-color: rgb(255, 85, 0);\n"
"    background-color: rgb(198, 178, 255);\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    font: 10pt \"MS Shell Dlg 2\";\n"
"    border-radius: 10px;\n"
"    border-color: beige;\n"
"}                   \n"
"QPushButton:enabled{\n"
"    background-color: rgb(198, 178, 255);\n"
"}                           \n"
"QPushButton:pressed{ \n"
"    background: red;\n"
"}                            \n"
"QPushButton:disabled{                             \n"
"    background-color: gray;                \n"
"}\n"
"QPushButton:hover{\n"
"    background-color: rgb(255, 85, 255);\n"
"}   ")
        self.Btn_CopyLink.setObjectName("Btn_CopyLink")
        self.Btn_AddTitel = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_AddTitel.setEnabled(False)
        self.Btn_AddTitel.setGeometry(QtCore.QRect(150, 20, 121, 61))
        self.Btn_AddTitel.setStyleSheet("QPushButton { \n"
"    color: rgb(0, 0, 127);\n"
"    selection-background-color: rgb(255, 85, 0);\n"
"    background-color: rgb(198, 178, 255);\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    font: 14pt \"MS Shell Dlg 2\";\n"
"    border-radius: 10px;\n"
"    border-color: beige;\n"
"}                   \n"
"QPushButton:enabled{\n"
"    background-color: rgb(198, 178, 255);\n"
"}                           \n"
"QPushButton:pressed{ \n"
"    background: red;\n"
"}                            \n"
"QPushButton:disabled{                             \n"
"    background-color: gray;                \n"
"}\n"
"QPushButton:hover{\n"
"    background-color: rgb(255, 85, 255);\n"
"}         ")
        self.Btn_AddTitel.setCheckable(True)
        self.Btn_AddTitel.setObjectName("Btn_AddTitel")
        self.lblDBTitel = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBTitel.setGeometry(QtCore.QRect(1150, 260, 31, 16))
        self.lblDBTitel.setObjectName("lblDBTitel")
        self.lblDBIAFDLink = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBIAFDLink.setGeometry(QtCore.QRect(1130, 350, 51, 16))
        self.lblDBIAFDLink.setObjectName("lblDBIAFDLink")
        self.lblDBPerformers = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBPerformers.setGeometry(QtCore.QRect(1110, 380, 61, 20))
        self.lblDBPerformers.setObjectName("lblDBPerformers")
        self.lblDBSceneCode = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBSceneCode.setGeometry(QtCore.QRect(1110, 520, 61, 16))
        self.lblDBSceneCode.setObjectName("lblDBSceneCode")
        self.lblDBRegie = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBRegie.setGeometry(QtCore.QRect(1140, 550, 31, 16))
        self.lblDBRegie.setObjectName("lblDBRegie")
        self.lblDBMovies = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBMovies.setGeometry(QtCore.QRect(1130, 580, 41, 16))
        self.lblDBMovies.setObjectName("lblDBMovies")
        self.lblDBSynopsis = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBSynopsis.setGeometry(QtCore.QRect(1120, 700, 51, 16))
        self.lblDBSynopsis.setObjectName("lblDBSynopsis")
        self.lblDBProDate = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBProDate.setGeometry(QtCore.QRect(1360, 520, 80, 20))
        self.lblDBProDate.setObjectName("lblDBProDate")
        self.tblWdg_Daten = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tblWdg_Daten.setGeometry(QtCore.QRect(29, 199, 1031, 761))
        self.tblWdg_Daten.setMaximumSize(QtCore.QSize(1100, 16777215))
        self.tblWdg_Daten.setTabletTracking(False)
        self.tblWdg_Daten.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.tblWdg_Daten.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tblWdg_Daten.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        self.tblWdg_Daten.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblWdg_Daten.setObjectName("tblWdg_Daten")
        self.tblWdg_Daten.setColumnCount(14)
        self.tblWdg_Daten.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignTop)
        self.tblWdg_Daten.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(12, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Daten.setHorizontalHeaderItem(13, item)
        self.tblWdg_Daten.horizontalHeader().setDefaultSectionSize(120)
        self.lblDBWebSideLink1 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBWebSideLink1.setGeometry(QtCore.QRect(1088, 290, 81, 16))
        self.lblDBWebSideLink1.setObjectName("lblDBWebSideLink1")
        self.lbl_DBWebSideLink1 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_DBWebSideLink1.setGeometry(QtCore.QRect(1180, 290, 680, 20))
        self.lbl_DBWebSideLink1.setStyleSheet("background-color: rgb(255, 250, 211);")
        self.lbl_DBWebSideLink1.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.lbl_DBWebSideLink1.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.lbl_DBWebSideLink1.setText("")
        self.lbl_DBWebSideLink1.setObjectName("lbl_DBWebSideLink1")
        self.lnEdit_DBTitel = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBTitel.setGeometry(QtCore.QRect(1180, 260, 681, 20))
        self.lnEdit_DBTitel.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBTitel.setObjectName("lnEdit_DBTitel")
        self.lnEdit_DBSceneCode = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBSceneCode.setGeometry(QtCore.QRect(1180, 520, 171, 20))
        self.lnEdit_DBSceneCode.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBSceneCode.setObjectName("lnEdit_DBSceneCode")
        self.lnEdit_DBProDate = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBProDate.setGeometry(QtCore.QRect(1450, 520, 161, 20))
        self.lnEdit_DBProDate.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBProDate.setObjectName("lnEdit_DBProDate")
        self.lnEdit_DBRegie = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBRegie.setGeometry(QtCore.QRect(1180, 550, 291, 20))
        self.lnEdit_DBRegie.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBRegie.setObjectName("lnEdit_DBRegie")
        self.Btn_IAFDLink = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_IAFDLink.setGeometry(QtCore.QRect(1084, 349, 91, 23))
        self.Btn_IAFDLink.setObjectName("Btn_IAFDLink")
        self.Btn_WebSide1 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_WebSide1.setGeometry(QtCore.QRect(1084, 289, 91, 23))
        self.Btn_WebSide1.setText("")
        self.Btn_WebSide1.setObjectName("Btn_WebSide1")
        self.lnEdit_DBRelease = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBRelease.setGeometry(QtCore.QRect(1710, 520, 151, 20))
        self.lnEdit_DBRelease.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBRelease.setObjectName("lnEdit_DBRelease")
        self.lblDBRelease = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBRelease.setGeometry(QtCore.QRect(1620, 520, 80, 20))
        self.lblDBRelease.setObjectName("lblDBRelease")
        self.Btn_CopyIAFD = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_CopyIAFD.setGeometry(QtCore.QRect(1180, 760, 101, 31))
        self.Btn_CopyIAFD.setObjectName("Btn_CopyIAFD")
        self.lblClipboard = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblClipboard.setGeometry(QtCore.QRect(1180, 810, 681, 101))
        self.lblClipboard.setStyleSheet("background-color: rgb(255, 253, 213);\n"
"")
        self.lblClipboard.setText("")
        self.lblClipboard.setObjectName("lblClipboard")
        self.txtEdit_DBMovies = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.txtEdit_DBMovies.setGeometry(QtCore.QRect(1180, 580, 680, 50))
        self.txtEdit_DBMovies.setStyleSheet("background-color: rgb(255, 250, 211);")
        self.txtEdit_DBMovies.setAcceptRichText(False)
        self.txtEdit_DBMovies.setObjectName("txtEdit_DBMovies")
        self.txtEdit_DBSynopsis = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.txtEdit_DBSynopsis.setGeometry(QtCore.QRect(1180, 700, 680, 50))
        self.txtEdit_DBSynopsis.setStyleSheet("background-color: rgb(255, 250, 211);")
        self.txtEdit_DBSynopsis.setAcceptRichText(False)
        self.txtEdit_DBSynopsis.setObjectName("txtEdit_DBSynopsis")
        self.Btn_DBUpdate = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_DBUpdate.setGeometry(QtCore.QRect(1290, 760, 101, 31))
        self.Btn_DBUpdate.setObjectName("Btn_DBUpdate")
        self.lbl_DatenSatz = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbl_DatenSatz.setGeometry(QtCore.QRect(220, 130, 81, 21))
        self.lbl_DatenSatz.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lbl_DatenSatz.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.lbl_DatenSatz.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.lbl_DatenSatz.setText("")
        self.lbl_DatenSatz.setObjectName("lbl_DatenSatz")
        self.lbllbl_DatenSatz = QtWidgets.QLabel(parent=self.centralwidget)
        self.lbllbl_DatenSatz.setGeometry(QtCore.QRect(160, 130, 61, 16))
        self.lbllbl_DatenSatz.setObjectName("lbllbl_DatenSatz")
        self.lnEdit_DBIAFDLink = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBIAFDLink.setGeometry(QtCore.QRect(1180, 350, 681, 20))
        self.lnEdit_DBIAFDLink.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBIAFDLink.setObjectName("lnEdit_DBIAFDLink")
        self.chkBox_IAFD = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.chkBox_IAFD.setGeometry(QtCore.QRect(1067, 350, 20, 20))
        self.chkBox_IAFD.setText("")
        self.chkBox_IAFD.setObjectName("chkBox_IAFD")
        self.txtEdit_DBTags = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.txtEdit_DBTags.setGeometry(QtCore.QRect(1180, 640, 680, 50))
        self.txtEdit_DBTags.setStyleSheet("background-color: rgb(255, 250, 211);")
        self.txtEdit_DBTags.setAcceptRichText(False)
        self.txtEdit_DBTags.setObjectName("txtEdit_DBTags")
        self.lblDBTags = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBTags.setGeometry(QtCore.QRect(1140, 640, 31, 16))
        self.lblDBTags.setObjectName("lblDBTags")
        self.tblWdg_Performers = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tblWdg_Performers.setGeometry(QtCore.QRect(1180, 380, 681, 131))
        self.tblWdg_Performers.setStyleSheet("background-color: rgb(255, 250, 211);")
        self.tblWdg_Performers.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.tblWdg_Performers.setLineWidth(0)
        self.tblWdg_Performers.setMidLineWidth(2)
        self.tblWdg_Performers.setObjectName("tblWdg_Performers")
        self.tblWdg_Performers.setColumnCount(3)
        self.tblWdg_Performers.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Performers.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Performers.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblWdg_Performers.setHorizontalHeaderItem(2, item)
        self.tblWdg_Performers.horizontalHeader().setDefaultSectionSize(226)
        self.Btn_AddPerformer = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_AddPerformer.setGeometry(QtCore.QRect(1100, 410, 75, 41))
        self.Btn_AddPerformer.setObjectName("Btn_AddPerformer")
        self.spinBox_vonVideo = QtWidgets.QSpinBox(parent=self.centralwidget)
        self.spinBox_vonVideo.setGeometry(QtCore.QRect(380, 130, 42, 22))
        self.spinBox_vonVideo.setMinimum(1)
        self.spinBox_vonVideo.setMaximum(600)
        self.spinBox_vonVideo.setObjectName("spinBox_vonVideo")
        self.spinBox_bisVideo = QtWidgets.QSpinBox(parent=self.centralwidget)
        self.spinBox_bisVideo.setGeometry(QtCore.QRect(450, 130, 61, 22))
        self.spinBox_bisVideo.setMinimum(2)
        self.spinBox_bisVideo.setMaximum(600)
        self.spinBox_bisVideo.setObjectName("spinBox_bisVideo")
        self.lblvonVideo = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblvonVideo.setGeometry(QtCore.QRect(350, 133, 21, 16))
        self.lblvonVideo.setObjectName("lblvonVideo")
        self.lblbisVideo = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblbisVideo.setGeometry(QtCore.QRect(430, 133, 21, 16))
        self.lblbisVideo.setObjectName("lblbisVideo")
        self.Btn_LastSide = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_LastSide.setGeometry(QtCore.QRect(530, 130, 75, 23))
        self.Btn_LastSide.setStyleSheet("QPushButton { \n"
"    color: rgb(0, 0, 127);\n"
"    selection-background-color: rgb(255, 85, 0);\n"
"    background-color: rgb(198, 178, 255);\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    font:8pt \"MS Shell Dlg 2\";\n"
"    border-radius: 10px;\n"
"    border-color: beige;\n"
"}                   \n"
"QPushButton:enabled{\n"
"    background-color: rgb(198, 178, 255);\n"
"}                           \n"
"QPushButton:pressed{ \n"
"    background: red;\n"
"}                            \n"
"QPushButton:disabled{                             \n"
"    background-color: gray;                \n"
"}\n"
"QPushButton:hover{\n"
"    background-color: rgb(255, 85, 255);\n"
"}    ")
        self.Btn_LastSide.setObjectName("Btn_LastSide")
        self.lblDBWebSideLink2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBWebSideLink2.setGeometry(QtCore.QRect(1088, 320, 81, 16))
        self.lblDBWebSideLink2.setObjectName("lblDBWebSideLink2")
        self.Btn_WebSide2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Btn_WebSide2.setGeometry(QtCore.QRect(1084, 319, 91, 23))
        self.Btn_WebSide2.setText("")
        self.Btn_WebSide2.setObjectName("Btn_WebSide2")
        self.lnEdit_DBWebSideLink2 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBWebSideLink2.setGeometry(QtCore.QRect(1180, 320, 681, 20))
        self.lnEdit_DBWebSideLink2.setStyleSheet("background-color: rgb(255, 250, 211);")
        self.lnEdit_DBWebSideLink2.setReadOnly(False)
        self.lnEdit_DBWebSideLink2.setObjectName("lnEdit_DBWebSideLink2")
        self.lnEdit_DBDauer_3 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBDauer_3.setGeometry(QtCore.QRect(1780, 549, 81, 20))
        self.lnEdit_DBDauer_3.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBDauer_3.setObjectName("lnEdit_DBDauer_3")
        self.lblDBSerie_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBSerie_3.setGeometry(QtCore.QRect(1485, 550, 31, 16))
        self.lblDBSerie_3.setObjectName("lblDBSerie_3")
        self.lnEdit_DBSerie_3 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lnEdit_DBSerie_3.setGeometry(QtCore.QRect(1515, 549, 221, 20))
        self.lnEdit_DBSerie_3.setStyleSheet("background-color: rgb(255, 253, 213);")
        self.lnEdit_DBSerie_3.setObjectName("lnEdit_DBSerie_3")
        self.lblDBDauer_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lblDBDauer_3.setGeometry(QtCore.QRect(1744, 550, 31, 16))
        self.lblDBDauer_3.setObjectName("lblDBDauer_3")
        self.tblWdg_Performers.raise_()
        self.Btn_Suchen.raise_()
        self.Btn_VideoData.raise_()
        self.Btn_IAFDLinken.raise_()
        self.Btn_VideoDB.raise_()
        self.lbl_Titel.raise_()
        self.lnEdit_Titel.raise_()
        self.lnEdit_Jahr.raise_()
        self.lblJahr.raise_()
        self.lblAFDLink.raise_()
        self.Btn_CopyLink.raise_()
        self.Btn_AddTitel.raise_()
        self.lblDBTitel.raise_()
        self.lblDBIAFDLink.raise_()
        self.lblDBPerformers.raise_()
        self.lblDBSceneCode.raise_()
        self.lblDBRegie.raise_()
        self.lblDBMovies.raise_()
        self.lblDBSynopsis.raise_()
        self.lblDBProDate.raise_()
        self.tblWdg_Daten.raise_()
        self.lblDBWebSideLink1.raise_()
        self.lbl_DBWebSideLink1.raise_()
        self.lnEdit_DBTitel.raise_()
        self.lnEdit_DBSceneCode.raise_()
        self.lnEdit_DBProDate.raise_()
        self.lnEdit_DBRegie.raise_()
        self.Btn_IAFDLink.raise_()
        self.Btn_WebSide1.raise_()
        self.lnEdit_DBRelease.raise_()
        self.lblDBRelease.raise_()
        self.Btn_CopyIAFD.raise_()
        self.lblClipboard.raise_()
        self.txtEdit_DBMovies.raise_()
        self.txtEdit_DBSynopsis.raise_()
        self.Btn_DBUpdate.raise_()
        self.lbl_DatenSatz.raise_()
        self.lbllbl_DatenSatz.raise_()
        self.lnEdit_DBIAFDLink.raise_()
        self.chkBox_IAFD.raise_()
        self.txtEdit_DBTags.raise_()
        self.lblDBTags.raise_()
        self.Btn_AddPerformer.raise_()
        self.spinBox_vonVideo.raise_()
        self.spinBox_bisVideo.raise_()
        self.lblvonVideo.raise_()
        self.lblbisVideo.raise_()
        self.Btn_LastSide.raise_()
        self.lblDBWebSideLink2.raise_()
        self.Btn_WebSide2.raise_()
        self.lnEdit_DBWebSideLink2.raise_()
        self.lnEdit_DBDauer_3.raise_()
        self.lblDBSerie_3.raise_()
        self.lnEdit_DBSerie_3.raise_()
        self.lblDBDauer_3.raise_()
        Haupt_Fenster.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=Haupt_Fenster)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1910, 21))
        self.menubar.setObjectName("menubar")
        Haupt_Fenster.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=Haupt_Fenster)
        self.statusbar.setObjectName("statusbar")
        Haupt_Fenster.setStatusBar(self.statusbar)

        self.retranslateUi(Haupt_Fenster)
        QtCore.QMetaObject.connectSlotsByName(Haupt_Fenster)

    def retranslateUi(self, Haupt_Fenster):
        _translate = QtCore.QCoreApplication.translate
        Haupt_Fenster.setWindowTitle(_translate("Haupt_Fenster", "HookupHotShot"))
        self.Btn_Suchen.setText(_translate("Haupt_Fenster", "Suchen"))
        self.Btn_VideoData.setText(_translate("Haupt_Fenster", "Video Daten \n"
" anzeigen lassen"))
        self.Btn_IAFDLinken.setText(_translate("Haupt_Fenster", "IAFD Linken"))
        self.Btn_VideoDB.setText(_translate("Haupt_Fenster", "Video DB \n"
"auffüllen"))
        self.lbl_Titel.setText(_translate("Haupt_Fenster", "Titel:"))
        self.lblJahr.setText(_translate("Haupt_Fenster", "Jahr:"))
        self.Btn_CopyLink.setText(_translate("Haupt_Fenster", "Copy Link"))
        self.Btn_AddTitel.setText(_translate("Haupt_Fenster", "Titel in DB\n"
" einfügen"))
        self.lblDBTitel.setText(_translate("Haupt_Fenster", "Titel:"))
        self.lblDBIAFDLink.setText(_translate("Haupt_Fenster", "IAFDLink:"))
        self.lblDBPerformers.setText(_translate("Haupt_Fenster", "Performers:"))
        self.lblDBSceneCode.setText(_translate("Haupt_Fenster", "SceneCode:"))
        self.lblDBRegie.setText(_translate("Haupt_Fenster", "Regie:"))
        self.lblDBMovies.setText(_translate("Haupt_Fenster", "Movies:"))
        self.lblDBSynopsis.setText(_translate("Haupt_Fenster", "Synopsis:"))
        self.lblDBProDate.setText(_translate("Haupt_Fenster", "Production Date:"))
        self.tblWdg_Daten.setSortingEnabled(True)
        item = self.tblWdg_Daten.horizontalHeaderItem(0)
        item.setText(_translate("Haupt_Fenster", "Titel"))
        item = self.tblWdg_Daten.horizontalHeaderItem(1)
        item.setText(_translate("Haupt_Fenster", "HookupHotShotLink"))
        item = self.tblWdg_Daten.horizontalHeaderItem(2)
        item.setText(_translate("Haupt_Fenster", "IAFDLink"))
        item = self.tblWdg_Daten.horizontalHeaderItem(3)
        item.setText(_translate("Haupt_Fenster", "Performers"))
        item = self.tblWdg_Daten.horizontalHeaderItem(4)
        item.setText(_translate("Haupt_Fenster", "Alias"))
        item = self.tblWdg_Daten.horizontalHeaderItem(5)
        item.setText(_translate("Haupt_Fenster", "Action"))
        item = self.tblWdg_Daten.horizontalHeaderItem(6)
        item.setText(_translate("Haupt_Fenster", "Release Datum"))
        item = self.tblWdg_Daten.horizontalHeaderItem(7)
        item.setText(_translate("Haupt_Fenster", "Production Date"))
        item = self.tblWdg_Daten.horizontalHeaderItem(8)
        item.setText(_translate("Haupt_Fenster", "Serie"))
        item = self.tblWdg_Daten.horizontalHeaderItem(9)
        item.setText(_translate("Haupt_Fenster", "Regie"))
        item = self.tblWdg_Daten.horizontalHeaderItem(10)
        item.setText(_translate("Haupt_Fenster", "Scene Code"))
        item = self.tblWdg_Daten.horizontalHeaderItem(11)
        item.setText(_translate("Haupt_Fenster", "Movies"))
        item = self.tblWdg_Daten.horizontalHeaderItem(12)
        item.setText(_translate("Haupt_Fenster", "Synopsis"))
        item = self.tblWdg_Daten.horizontalHeaderItem(13)
        item.setText(_translate("Haupt_Fenster", "Tags"))
        self.lblDBWebSideLink1.setText(_translate("Haupt_Fenster", "Hookup Hotshots:"))
        self.Btn_IAFDLink.setText(_translate("Haupt_Fenster", "IAFD"))
        self.lblDBRelease.setText(_translate("Haupt_Fenster", "Release Datum:"))
        self.Btn_CopyIAFD.setText(_translate("Haupt_Fenster", "in die\n"
"Zwischenablage"))
        self.Btn_DBUpdate.setText(_translate("Haupt_Fenster", "Update in die\n"
"Datenbank"))
        self.lbllbl_DatenSatz.setText(_translate("Haupt_Fenster", "Datensatz:"))
        self.lnEdit_DBIAFDLink.setPlaceholderText(_translate("Haupt_Fenster", "Press \"c\" for get IAFD Link"))
        self.lblDBTags.setText(_translate("Haupt_Fenster", "Tags:"))
        item = self.tblWdg_Performers.horizontalHeaderItem(0)
        item.setText(_translate("Haupt_Fenster", "Name"))
        item = self.tblWdg_Performers.horizontalHeaderItem(1)
        item.setText(_translate("Haupt_Fenster", "Alias"))
        item = self.tblWdg_Performers.horizontalHeaderItem(2)
        item.setText(_translate("Haupt_Fenster", "Action"))
        self.Btn_AddPerformer.setText(_translate("Haupt_Fenster", "Add \n"
"Performer"))
        self.lblvonVideo.setText(_translate("Haupt_Fenster", "von:"))
        self.lblbisVideo.setText(_translate("Haupt_Fenster", "bis"))
        self.Btn_LastSide.setText(_translate("Haupt_Fenster", "Letzte Seite"))
        self.lblDBWebSideLink2.setText(_translate("Haupt_Fenster", "Evil Angel:"))
        self.lblDBSerie_3.setText(_translate("Haupt_Fenster", "Serie:"))
        self.lblDBDauer_3.setText(_translate("Haupt_Fenster", "Dauer:"))