# Form implementation generated from reading ui file 'e:\Python\Python_WORK\Datei_Info_Creator\gui\uic_imports\dialog_ui\dialog_update_performer-log.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        Dialog.resize(400, 317)
        Dialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_update_performer_log = QtWidgets.QLabel(parent=Dialog)
        self.lbl_update_performer_log.setStyleSheet("background-color: #FFFDD5")
        self.lbl_update_performer_log.setText("")
        self.lbl_update_performer_log.setWordWrap(True)
        self.lbl_update_performer_log.setObjectName("lbl_update_performer_log")
        self.gridLayout.addWidget(self.lbl_update_performer_log, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Update Performer Log-File:"))