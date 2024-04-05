from PyQt6 import uic
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMenu, QMainWindow

from urllib.parse import urlparse
from pathlib import Path

from utils.database_settings.database_for_darsteller import DB_Darsteller, VideoData

from config import ADD_PERFORMER_UI, ID_MERGE_PERFORMER_UI, ADD_NEW_PERFORMER_UI, ADD_NAMESLINK_PERFORMER_UI

class PerformerAddDel(QDialog):    
    def __init__(self, parent, menu=None, Main= None): # von wo es kommt: None = add name und ordner       
        super(PerformerAddDel,self).__init__(Main) 
        self.Main = Main
        self.cmenu=parent 
        if isinstance(self.cmenu, QMenu):
            self.cmenu.dialog_shown = True
        ### ------- Performer Tabelle: Merge IDs ------------------------------------------------------ ###
        if menu=="merge": 
            uic.loadUi(ID_MERGE_PERFORMER_UI, self)              
            self.accepted.connect(self.accepted_id_merge_performer)
            self.timer_start("id","id")
        ### ------------------------------------------------------------------------------------------- ###

        ### ------- Performer Link Tabelle: Zeile für eine neuen Performer Datensatz anlegen ---------- ###
        elif menu=="add_new_performer":                       
            if self.Main.tblWdg_performer_links.rowCount() <= 1:
                self.Main.lbl_db_status.setText("Nur '1' Eintrag in der Tabelle")
                return
            uic.loadUi(ADD_NEW_PERFORMER_UI, self)  
            self.lnEdit_name.setText(self.Main.lnEdit_performer_info.text())
            self.accepted.connect(self.accepted_add_new_performer)
            self.timer_start("name","name")
            self.timer_start("ordner","name")
        ### ------------------------------------------------------------------------------------------- ###  

        ### ------- Performer Link Tabelle: neuen Link eintragen --------------------------- ###     
        elif menu == "add_new_nameslink":            
            uic.loadUi(ADD_NAMESLINK_PERFORMER_UI, self)
            self.lbl_artist_id_db.setText(self.Main.grpBox_performer_name.title().replace("Performer-Info ID: ",""))           
            self.accepted.connect(self.accepted_add_new_nameslink)
            #self.Btn_image_scrape.clicked.connect(self.image_scrape)
            self.Btn_id_merge.clicked.connect(self.button_accepted_id_merge_performer)
            self.timer_start("link","nameslink") 
        ### ------- Performer Tabelle: Zeile/Namen neuen Datensatz anlegen ---------------------------- ###
        else:
            uic.loadUi(ADD_PERFORMER_UI, self)              
            self.accepted.connect(self.accepted_add_perfomer) 
        ### ------------------------------------------------------------------------------------------- ###                          
        self.move(self.cmenu.context_menu.mapToGlobal(self.cmenu.context_menu.rect().topLeft())- QPoint(0, 30))
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""") # Use the QMainWindow's background color
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  
        self.rejected.connect(lambda: (setattr(self.cmenu, 'dialog_shown', False), self.close())) 
        self.exec()
        self.old_pos = QPoint()
    ### ----------------- Fenster per Maus bewegen ------------------------- ###
    def mousePressEvent(self, event):        
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition()

    def mouseMoveEvent(self, event):        
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition() - self.old_pos            
            self.move(self.x() + int(delta.x()), self.y() + int(delta.y()))
            self.old_pos = event.globalPosition()
    ### ------------------------------------------------------------ ###
            
    ### ----------------- Hilfs Funktionen ------------------------- ###
    def timer_start(self, widget: str, connect_widget: str) -> None:
        getattr(self, f"lnEdit_{widget}").textChanged.connect(lambda: self.timer.start(800))  # 0.8 sekunden wartet    
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(getattr(self, f"check_{connect_widget}"))
    
    def lineedit_error(self, message: str, widget: str, error):  
        farbe = "#FF0000" if error else "#3DE000"     
        getattr(self, f"lbl_{widget}_db").setText(message)
        getattr(self, f"lnEdit_{widget}").setStyleSheet(f'background-color: {farbe}')      
        QTimer.singleShot(500, lambda :getattr(self, f"lnEdit_{widget}").setStyleSheet('background-color:'))        
        QTimer.singleShot(1000, lambda :getattr(self, f"lnEdit_{widget}").setStyleSheet(f'background-color: {farbe}'))
        QTimer.singleShot(3000, lambda :(getattr(self, f"lnEdit_{widget}").setStyleSheet('background-color:')))
    ### ------------------------------------------------------------ ###
        
    def accepted_add_perfomer(self): 
        name=self.lnEdit_name.text()
        ordner=self.lnEdit_ordner.text()
        sex=self.cBox_performer_gender.currentIndex()+1
        if name:
            self.close()
        if not ordner:
            ordner=name  
        self.cmenu.dialog_shown = False          
        self.cmenu.add_name_and_ordner.emit(name, ordner, sex)
        self.close() 

    ### ----------------- Performer Tabelle: Merge IDs ------------------------------ ###
    def accepted_id_merge_performer(self):
        datenbank_darsteller = DB_Darsteller(self.Main)
        artist_id=int(self.lnEdit_id.text())
        current_row = self.Main.tblWdg_performer.currentRow()
        first_artist_id = int(self.Main.tblWdg_performer.item(current_row,0).text())
        name=datenbank_darsteller.get_name_from_id(artist_id)
        if name:
            self.lbl_id_db.setText(f"{artist_id}")
        else:
            self.lbl_id_db.setText(f"{0}")
        #self.cmenu.dialog_shown = False
        artist_id=int(self.lbl_id_db.text())       
        self.cmenu.merge_ids.emit(first_artist_id, artist_id)
        self.close()   

    def check_id(self):
        artist_id=int(self.lnEdit_id.text())
        if not artist_id:
            self.lineedit_error("keine ID eingegeben !","id", error=True)
        else:
            datenbank_darsteller = DB_Darsteller(self.Main)
            name=datenbank_darsteller.get_name_from_id(artist_id)            
            if not name:
                self.lineedit_error(f"{artist_id} nicht in der Datenbank gefunden !","id", error=True)
                self.lbl_id_db.setText("")
            else:
                self.lbl_id_db.setText(f"{artist_id}")
                self.lbl_name_db.setText(name)

    ### ------ Performer Tabelle: Zeile für eine neuen Performer Datensatz anlegen ------------------------ ###
    def accepted_add_new_performer(self):        
        name=self.lnEdit_name.text()
        if not name:
            self.lineedit_error("keinen Namen eingegeben !","name", error=True)        
        else:
            if self.lnEdit_ordner.text() == "":
                self.lnEdit_ordner.setText(name)
            ordner=self.lnEdit_ordner.text()
            datenbank_darsteller = DB_Darsteller(self.Main)
            artist_id = datenbank_darsteller.get_artistid_from_name_ordner(name, ordner)
            iafd_link = self.lnEdit_iafdlink.text()
            if iafd_link:
                artist_id = datenbank_darsteller.get_artistid_from_nameslink(iafd_link)
            if artist_id == -1: # neuen Darsteller anlegen                
                artist_id = datenbank_darsteller.add_artistid_from_name_ordner(name, ordner)
            self.cmenu.add_artist.emit(artist_id, iafd_link, name, ordner)        
            self.close()

    def check_name(self):
        name=self.lnEdit_name.text() 
        if not name:
            self.lineedit_error("keinen Namen eingegeben !","name", error=True)
        else:
            if self.lnEdit_ordner.text() == "":
                self.lnEdit_ordner.setText(name)
            ordner=self.lnEdit_ordner.text()
            datenbank_darsteller = DB_Darsteller(self.Main)
            if self.lnEdit_iafdlink.text():
                artist_id = datenbank_darsteller.get_artistid_from_nameslink(self.lnEdit_iafdlink.text())
                if artist_id != -1: # hat etwas in der datenbank gefunden
                    nameslink_iafd = datenbank_darsteller.get_nameslink_dataset_from_artistid(artist_id)
                    ordner = Path(nameslink_iafd["Image"]).parent.name
                    self.lnEdit_ordner.setText(ordner)
            errview = datenbank_darsteller.get_minidatas_from_ordner(ordner) 
            artist_data_json=VideoData().load_from_json()           
            if not artist_data_json:
                self.lineedit_error(f"Wird neu angelegt", "name", error=False)
                self.tblWdg_datenbank.setRowCount(0)
            else: 
                self.lineedit_error(f"{len(artist_data_json)} mal '{ordner}' gefunden", "name", error=False)         
                for zeile, artist_data in enumerate(artist_data_json):            
                    self.tblWdg_datenbank.setRowCount(zeile+1) 
                    self.tblWdg_datenbank.setItem(zeile,0,QTableWidgetItem(f'{artist_data["ArtistID"]}'))                               
                    self.tblWdg_datenbank.setItem(zeile,1,QTableWidgetItem(artist_data["Name"])) 
                    self.tblWdg_datenbank.setItem(zeile,2,QTableWidgetItem(artist_data["Ordner"]))
                    self.tblWdg_datenbank.resizeColumnsToContents()            
    ### ------------------------------------------------------------------------------------------- ###
            
    ### ------- Perfomer Links Tabelle: Zeile hinzufügen ------------------------------------------ ###
    def accepted_add_new_nameslink(self):
        datenbank_darsteller = DB_Darsteller(self.Main)
        link=self.lnEdit_link.text()  
        names_id = datenbank_darsteller.get_namesid_from_nameslink(link)
        is_vorhanden=False                
        for row in range(self.Main.tblWdg_performer_links.rowCount()):
            if self.Main.tblWdg_performer_links.item(row, 0).text() == names_id:
                is_vorhanden=True
                break
        artist_id: int= -1
        names_link_satz: dict={}
        studio_link = f"{urlparse(link).scheme}://{urlparse(link).netloc}/"                       
        studio_id = datenbank_darsteller.get_studio_id_from_baselink(studio_link)
        if link is None:
            self.lineedit_error(f"kein Link eingegeben !", "link", error=True)
        elif studio_id == -1:
            self.lineedit_error(f"BaseLink {studio_link} nicht in der Datenbank gefunden !", "link", error=True)            
        else:   
            if not (names_id and is_vorhanden):
                self.Main.lbl_db_status.setText("")
                self.Main.lbl_db_status.setStyleSheet('background-color:')
                artist_id = int(self.lbl_artist_id_db.text())            
                names_link_satz = self.set_names_link_satz_in_dict(link)
            if isinstance(self.cmenu, QMenu):
                self.cmenu.add_namesid.emit(artist_id, names_link_satz, studio_id) 
            elif isinstance(self.cmenu, QMainWindow): 
                self.cmenu.add_namesid.emit(artist_id, names_link_satz, studio_id)         
            self.close()
    
    def check_nameslink(self):
        link=self.lnEdit_link.text()
        if link:
            datenbank_darsteller = DB_Darsteller(self.Main)
            names_id = datenbank_darsteller.get_namesid_from_nameslink(link)
            studio_link = f"{urlparse(link).scheme}://{urlparse(link).netloc}/"                       
            studio_id = datenbank_darsteller.get_studio_id_from_baselink(studio_link)
            is_vorhanden=False
            for row in range(self.Main.tblWdg_performer_links.rowCount()):
                if self.Main.tblWdg_performer_links.item(row, 0).text() == names_id:
                    is_vorhanden=True 
            self.Main.lbl_db_status.setText("")
            self.Main.lbl_db_status.setStyleSheet('background-color:')
            if not names_id:                
                self.lineedit_error(f"{link} nicht in der Datenbank gefunden !", "link", error=False)                
            if studio_id == -1:
                self.lineedit_error(f"BaseLink {studio_link} nicht in der Datenbank gefunden !", "link", error=True)
            elif names_id and is_vorhanden == False:                
                self.Btn_id_merge.setEnabled(True)
                daten_satz = datenbank_darsteller.get_nameslink_dataset_from_namesid(names_id)
                if daten_satz:
                    artist_id = datenbank_darsteller.get_artistid_from_nameslink(link)
                    self.lbl_artist_id2_db.setText(f"{artist_id}")
                    self.lbl_names_id_db.setText(f"{daten_satz[0]}")
                    self.lbl_link_db.setText(daten_satz[1])
                    self.lbl_ordner_db.setText(daten_satz[2])                
                    self.lbl_alias_db.setText(daten_satz[3])
            elif is_vorhanden:
                self.lineedit_error(f"{link} schon in der Performer Links Tabelle !", "link", error=True)
                self.lnEdit_link.setText("")

    def button_accepted_id_merge_performer(self):
        #self.cmenu.dialog_shown = False
        artist_id1 = int(self.lbl_artist_id_db.text())
        artist_id2 = int(self.lbl_artist_id2_db.text())
        self.cmenu.merge_ids.emit(artist_id1, artist_id2)
        self.close()
    ### ------------------------------------------------------------------------------------------- ###
    
    def set_names_link_satz_in_dict(self, link):
        return { "NamesID": None,
                "Link": link,
                "Image": None,
                "Alias": None   }
         

if __name__ == '__main__':
    app = QApplication([])
    
    mein_dialog = PerformerAddDel()
    # Zeige den Dialog an
    mein_dialog.show()
    import sys
    sys.exit(app.exec())
