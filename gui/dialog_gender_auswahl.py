from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from config import GENDER_AUSWAHL_UI

class GenderAuswahl(QDialog):
    def __init__(self, parent, show=True): # von wo es kommt 
        super(GenderAuswahl,self).__init__(parent) 
        self.Main = parent
        self.gender_property = self.Main.Btn_performers_gender.property("gender")

        if show:
            uic.loadUi(GENDER_AUSWAHL_UI, self)
            standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
            self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  
            self.Btn_female.clicked.connect(self.female_auswahl)
            self.Btn_male.clicked.connect(self.male_auswahl)
            self.Btn_trans.clicked.connect(self.trans_auswahl)
    
    def female_auswahl(self):
        self.Main.Btn_performers_gender.setIcon(QIcon(":Buttons\_buttons\gender\person-weiblich.png")) 
        self.Main.Btn_performers_gender.setProperty("gender", "female")              
        self.Main.Btn_IAFD_perfomer_suche.setEnabled(True)
        self.Main.Btn_IAFD_perfomer_suche.setToolTip("erstellt ein IAFD Link und setzt in die Maske")
        self.check_gender_changes()
        self.close()
    
    def male_auswahl(self):
        self.Main.Btn_performers_gender.setIcon(QIcon(":Buttons\_buttons\gender\person-maennlich.png"))
        self.Main.Btn_performers_gender.setProperty("gender", "male")
        self.Main.Btn_IAFD_perfomer_suche.setEnabled(True)
        self.Main.Btn_IAFD_perfomer_suche.setToolTip("erstellt ein IAFD Link und setzt in die Maske")
        self.check_gender_changes()        
        self.close()
    
    def trans_auswahl(self):
        self.Main.Btn_performers_gender.setIcon(QIcon(":Buttons\_buttons\gender\person-trans.png"))
        self.Main.Btn_performers_gender.setProperty("gender", "trans")
        self.Main.Btn_IAFD_perfomer_suche.setEnabled(True)
        self.Main.Btn_IAFD_perfomer_suche.setToolTip("erstellt ein IAFD Link und setzt in die Maske")
        self.check_gender_changes()
        self.close()

    def check_gender_changes(self):
        if self.Main.Btn_performers_gender.property("gender") != self.gender_property:
            self.Main.Btn_DBArtist_Update.setEnabled(True)


    def get_gender_for_iafdlink(self): 
        print(self.Main.Btn_performers_gender.property("gender"))       
        if self.Main.Btn_performers_gender.property("gender") == "male":
            return "m"        
        else:
            return "f"
        
    def get_gender_from_button(self): 
        if self.Main.Btn_performers_gender.property("gender") == "male":
            return 2
        elif self.Main.Btn_performers_gender.property("gender") == "female":
            return 1
        else:
            return 3
        
    def set_icon_in_gender_button(self, gender):
        gender = int(gender) if isinstance(gender,str) and gender.isdigit() else 1
        if gender == 1:
            self.female_auswahl()
        elif gender == 2:
            self.male_auswahl()
        else:
            self.trans_auswahl()


if __name__ == '__main__':
    GenderAuswahl(QDialog)