# Form implementation generated from reading ui file 'e:\Python\Python_WORK\Datei_Info_Creator\gui\uic_imports\url_input_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.5.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_dialog_seturl(object):
    def setupUi(self, dialog_seturl):
        dialog_seturl.setObjectName("dialog_seturl")
        dialog_seturl.resize(415, 103)
        dialog_seturl.setSizeGripEnabled(True)
        dialog_seturl.setModal(True)
        self.lnEdit_website_url = QtWidgets.QLineEdit(parent=dialog_seturl)
        self.lnEdit_website_url.setGeometry(QtCore.QRect(10, 25, 400, 25))
        self.lnEdit_website_url.setMinimumSize(QtCore.QSize(400, 25))
        self.lnEdit_website_url.setStyleSheet("background-color: #FFFDD5;")
        self.lnEdit_website_url.setObjectName("lnEdit_website_url")
        self.Btn_link_copy = QtWidgets.QPushButton(parent=dialog_seturl)
        self.Btn_link_copy.setGeometry(QtCore.QRect(386, 27, 20, 20))
        self.Btn_link_copy.setMinimumSize(QtCore.QSize(20, 20))
        self.Btn_link_copy.setMaximumSize(QtCore.QSize(20, 20))
        self.Btn_link_copy.setStyleSheet("background-color: #FFFDD5;")
        self.Btn_link_copy.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/labels/_labels/copy_clip.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.Btn_link_copy.setIcon(icon)
        self.Btn_link_copy.setAutoDefault(False)
        self.Btn_link_copy.setFlat(True)
        self.Btn_link_copy.setObjectName("Btn_link_copy")
        self.layoutWidget = QtWidgets.QWidget(parent=dialog_seturl)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 60, 402, 37))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblstatus = QtWidgets.QLabel(parent=self.layoutWidget)
        self.lblstatus.setMinimumSize(QtCore.QSize(35, 25))
        self.lblstatus.setMaximumSize(QtCore.QSize(35, 25))
        self.lblstatus.setObjectName("lblstatus")
        self.horizontalLayout.addWidget(self.lblstatus)
        self.lbl_status = QtWidgets.QLabel(parent=self.layoutWidget)
        self.lbl_status.setMinimumSize(QtCore.QSize(40, 25))
        self.lbl_status.setMaximumSize(QtCore.QSize(40, 25))
        self.lbl_status.setStyleSheet("background-color: #FFFDD5;")
        self.lbl_status.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.lbl_status.setText("")
        self.lbl_status.setObjectName("lbl_status")
        self.horizontalLayout.addWidget(self.lbl_status)
        self.lblstatus_icon = QtWidgets.QLabel(parent=self.layoutWidget)
        self.lblstatus_icon.setMinimumSize(QtCore.QSize(20, 20))
        self.lblstatus_icon.setMaximumSize(QtCore.QSize(20, 20))
        self.lblstatus_icon.setText("")
        self.lblstatus_icon.setObjectName("lblstatus_icon")
        self.horizontalLayout.addWidget(self.lblstatus_icon)
        self.lbl_scrape_infos = QtWidgets.QLabel(parent=self.layoutWidget)
        self.lbl_scrape_infos.setMinimumSize(QtCore.QSize(200, 25))
        self.lbl_scrape_infos.setMaximumSize(QtCore.QSize(200, 25))
        self.lbl_scrape_infos.setStyleSheet("background-color: #FFFDD5;")
        self.lbl_scrape_infos.setText("")
        self.lbl_scrape_infos.setObjectName("lbl_scrape_infos")
        self.horizontalLayout.addWidget(self.lbl_scrape_infos)
        self.btn_scrape = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.btn_scrape.setMinimumSize(QtCore.QSize(45, 30))
        self.btn_scrape.setMaximumSize(QtCore.QSize(45, 30))
        self.btn_scrape.setObjectName("btn_scrape")
        self.horizontalLayout.addWidget(self.btn_scrape)
        self.Btn_OK = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.Btn_OK.setMinimumSize(QtCore.QSize(30, 30))
        self.Btn_OK.setMaximumSize(QtCore.QSize(30, 30))
        self.Btn_OK.setObjectName("Btn_OK")
        self.horizontalLayout.addWidget(self.Btn_OK)
        self.Btn_close = QtWidgets.QPushButton(parent=dialog_seturl)
        self.Btn_close.setGeometry(QtCore.QRect(390, 2, 23, 23))
        self.Btn_close.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/labels/_labels/fenster-schliessen.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.Btn_close.setIcon(icon1)
        self.Btn_close.setIconSize(QtCore.QSize(25, 25))
        self.Btn_close.setFlat(True)
        self.Btn_close.setObjectName("Btn_close")
        self.lbl_bio_logo = QtWidgets.QLabel(parent=dialog_seturl)
        self.lbl_bio_logo.setGeometry(QtCore.QRect(14, 3, 50, 25))
        self.lbl_bio_logo.setMinimumSize(QtCore.QSize(50, 25))
        self.lbl_bio_logo.setMaximumSize(QtCore.QSize(50, 25))
        self.lbl_bio_logo.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.lbl_bio_logo.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.lbl_bio_logo.setText("")
        self.lbl_bio_logo.setObjectName("lbl_bio_logo")

        self.retranslateUi(dialog_seturl)
        QtCore.QMetaObject.connectSlotsByName(dialog_seturl)

    def retranslateUi(self, dialog_seturl):
        _translate = QtCore.QCoreApplication.translate
        dialog_seturl.setWindowTitle(_translate("dialog_seturl", "Dialog"))
        self.lnEdit_website_url.setPlaceholderText(_translate("dialog_seturl", "gebe eine URL ein"))
        self.Btn_link_copy.setToolTip(_translate("dialog_seturl", "kopiert den Link in die Ziwschenablage"))
        self.lblstatus.setText(_translate("dialog_seturl", "Status:"))
        self.btn_scrape.setText(_translate("dialog_seturl", "Scrape"))
        self.Btn_OK.setText(_translate("dialog_seturl", "OK"))
