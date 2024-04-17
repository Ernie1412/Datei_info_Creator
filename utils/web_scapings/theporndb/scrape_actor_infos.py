from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QTableWidgetItem
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer, QModelIndex

import re

from utils.threads.scrape_api_theporndb_thread import ScrapeAPIThePornDBThread
from utils.web_scapings.theporndb.api_prepare_for_gui import API_Actors
from utils.web_scapings.theporndb.upload_performer_in_theporndb import UploadPerformer
from utils.web_scapings.theporndb.show_last_log_dialog import ShowLogDialogThePornDB
from utils.web_scapings.theporndb.set_actor_infos_in_widget import SetActorInfos
from utils.database_settings.database_for_darsteller import DB_Darsteller
from gui.get_avaible_labels import GetLabels
from utils.web_scapings.theporndb.helpers.scrape_actor_helper_theporndb import date_formarted, get_image_counter, check_avaible_bio_websites
from gui.helpers.message_show import MsgBox

from config import SRACPE_ACTOR_INFOS_UI

class ScrapeActorInfos(QDialog):
    def __init__(self, api_link, MainWindow, parent): # von wo es kommt  
        super(ScrapeActorInfos, self).__init__(parent)
        self.Main = MainWindow 
        self.set_actor = SetActorInfos(self)
        self.image_counter = 0
        self.apiThread = None 
         
        self.search = False 
        self.api_link = api_link        
        if not api_link.startswith('https://api.theporndb.net/'):
            self.search = True
            self.api_link = f"https://api.theporndb.net/performers?q={api_link}"

        uic.loadUi(SRACPE_ACTOR_INFOS_UI, self) 
        self.uploader = UploadPerformer(self.Main, self)        
        self.apiThread = None       
        self.tblWdg_search_result_actors.itemClicked.connect(self.onItemClicked)
        self.Btn_get_DB_data_in_dialog.clicked.connect(self.get_DB_data_in_dialog)
        self.Btn_set_DB_data_in_dialog.clicked.connect(self.set_DB_data_in_dialog)
        self.Btn_upload_datas.clicked.connect(self.uploader.upload_performer)
        self.Btn_add_mydb_item.clicked.connect(self.add_item_in_mydb_table)
        self.Btn_del_mydb_item.clicked.connect(self.del_item_in_mydb_table)
        self.Btn_refresh_mydb_item.clicked.connect(self.set_actor.set_medialink_from_mydb_in_table)
        self.chkBox_actor_rasse.stateChanged.connect(self.set_actor_ethnicity_activ)
        self.chkBox_actor_eye.stateChanged.connect(self.set_actor_eye_activ)
        self.Btn_accept.clicked.connect(self.accept)
        self.Btn_show_last_log.clicked.connect(self.show_last_log)
        self.lnEdit_performer_id.textChanged.connect(lambda index :self.Btn_set_DB_data_in_dialog.setEnabled(bool(self.lnEdit_performer_id.text()))) 
        
    def showEvent(self, event):
        self.apiThread = ScrapeAPIThePornDBThread(self.api_link) 
        self.apiThread.apiFinished.connect(self.apiFinished) 
        self.apiThread.start()

    def apiFinished(self, api_data): 
        self.apiThread.quit()
        self.apiThread.wait()   
        self.get_api_actors_infos(api_data)

    def get_api_actors_infos(self, api_data): 
        if api_data.get('message') == 'Unauthenticated.':
            MsgBox(self.Main, "'Unauthenticated' Du bist nicht angemeldet. Bitte melde dich an.","w")
            self.reject() 
            return
        elif api_data.get('message') == 'key missing':
            MsgBox(self.Main, "kein API Key vorhanden. Setze einen in den Einstellungen !","w")
            self.reject()
            return
        elif not api_data and api_data.get('data') == []:
            MsgBox(self.Main, f"keine Daten gefunden für {self.api_link}!","w")
            self.reject()
            return
        else:             
            self.show()
            self.set_api_infos_ui(api_data)

    def get_DB_data_in_dialog(self):
        line, text = self.get_all_widgets()
        for lineedit in line:
            lnEdit = getattr(self, f"lnEdit_performer_{lineedit}")
            if lnEdit.activated:                
                if lineedit == "career_start_year":
                    start, end = self.formarted_year(getattr(self.Main, f"lnEdit_performer_activ").text())
                    lnEdit.setText(start)
                    end, bolean = ("0", False) if int(end) >= 2022 else (end, True)
                    getattr(self, f"lnEdit_performer_career_end_year").setText(end)
                    getattr(self, f"lnEdit_performer_career_end_year").setActivated(bolean)                   
                else:
                    lnEdit.setText(getattr(self.Main, f"lnEdit_performer_{lineedit}").text())                               
        for textedit in text:
            txtEdit = getattr(self, f"txtEdit_performer_{textedit}")
            if txtEdit.activated:
                txtEdit.setPlainText(getattr(self.Main, f"txtEdit_performer_{textedit}").toPlainText()) 
        self.set_nationality_in_lineedit()        

    def set_nationality_in_lineedit(self):
        nationality = []
        for nation in range(7):
            label = getattr(self.Main, f"lbl_performer_nation_{nation}")
            if label.property("nation"):
                nation_ger = label.property("nation")
                nation_eng = self.from_deutsch_in_englisch_nation(nation_ger)
                nationality.append(nation_eng) 
        nations_eng = ", ".join(nationality)
        self.lnEdit_performer_nationality.setText(nations_eng)
        self.lnEdit_performer_nationality.setActivated(True)

    def from_deutsch_in_englisch_nation(self, nation_ger):
        database_for_darsteller = DB_Darsteller(self.Main)
        return database_for_darsteller.get_nation_ger_to_english(nation_ger)

    def formarted_year(self, text):
        match = re.search(r"\d{4}-\d{4}", text)
        return match.group(0).split("-") if match else ('0', '0')
    
    def set_DB_data_in_dialog(self):
        line, text = self.get_all_widgets()
        for lineedit in line:
            lnEdit = getattr(self, f"lnEdit_performer_{lineedit}")
            if lnEdit.activated:
                if lineedit in ["career_start_year", "career_end_year"]:                
                    start_end = self.formarted_year_for_dialog(getattr(self.Main, f"lnEdit_performer_activ").text())                
                    start = getattr(self, f"lnEdit_performer_career_start_year").text()
                    getattr(self, f"lnEdit_performer_career_start_year").setActivated(False)
                    end = getattr(self, f"lnEdit_performer_career_end_year").text()  
                    getattr(self, f"lnEdit_performer_career_end_year").setActivated(False)   
                    getattr(self.Main, f"lnEdit_performer_activ").setText(f"von: {start_end}-{start_end}")
                else:
                    lnEdit_main = getattr(self.Main, f"lnEdit_performer_{lineedit}").setText(lnEdit.text())                    
                    lnEdit.setActivated(False)                
        for textedit in text:
            txtEdit_main = getattr(self.Main, f"txtEdit_performer_{textedit}")
            txtEdit = getattr(self, f"txtEdit_performer_{textedit}")
            if txtEdit.activated:
                txtEdit_main.setPlainText(txtEdit.toPlainText())
                txtEdit.setActivated(False)               
        #### ----------------- set api link in Button --------------------- ####
        uuid = self.lnEdit_performer_uuid.text()
        if uuid:
            self.Main.Btn_performer_in_ThePornDB.setToolTip(f"https://api.theporndb.net/performers/{uuid}")
            self.lnEdit_performer_uuid.setActivated(False)
            check_avaible_bio_websites(self.Main) 
        self.set_actor_image_in_dialog()

    def set_actor_image_in_dialog(self):
        if hasattr(self, 'lbl_image0'):
            label = self.lbl_image0
            self.Main.lbl_theporndb_image.setPixmap(label.pixmap())
            self.Main.lbl_theporndb_image.setToolTip(label.toolTip())            
        else:
            self.Main.lbl_theporndb_image.setPixmap(QPixmap(":/labels/_labels/kein-bild.jpg"))
            self.Main.lbl_theporndb_image.setToolTip("ThePornDB: kein Bild vorhanden")
        self.Main.lbl_theporndb_image.setProperty("name", self.lnEdit_performer_name.text().replace(" ", "-"))

        self.Main.stacked_webdb_images.setCurrentIndex(1)

    def set_actor_ethnicity_activ(self):
        if self.chkBox_actor_rasse.isChecked():
            self.cBox_performer_rasse.setStyleSheet("background-color: #d4ffc4;")
        else:
            self.cBox_performer_rasse.setStyleSheet("background-color: #FFFDD5;")

    def set_actor_eye_activ(self):
        if self.chkBox_actor_eye.isChecked():
            self.cBox_performer_eye.setStyleSheet("background-color: #d4ffc4;")
        else:
            self.cBox_performer_eye.setStyleSheet("background-color: #FFFDD5;") 

    def get_all_widgets(self):
        lineedits = ["birthplace", "birthday", "boobs", "height", "weight", "career_start_year"]
        textedit = ["piercing", "tattoo"]
        return lineedits, textedit

    def set_api_infos_ui(self, api_data):                
        uuid, search_count = API_Actors.get_actor_data(api_data, 'id')
        
        self.lnEdit_performer_uuid.setText(uuid)
        if self.search and search_count >0:
            self.lbl_search_counter.setText(f"gefundene Personen: {search_count}") 
            self.set_search_result_in_table(api_data)                                    
        else:
            self.image_counter = get_image_counter() 
            id = API_Actors.get_actor_data(api_data, '_id')[0] 
            if not id:
                self.lbl_status_message.setText(f"keine Daten gefunden für {self.api_link}")                
                return            
            self.lnEdit_performer_id.setText(f"{id}")           
            self.set_actor.set_gender_icon(API_Actors.get_actor_extras(api_data, 'gender'))
            date1, date2 = date_formarted(API_Actors.get_actor_extras(api_data,'birthday'))                   
            self.lnEdit_performer_birthday.setText(date2)            
            self.lnEdit_performer_birthplace.setText(API_Actors.get_actor_extras(api_data, 'birthplace'))
            self.lbl_actor_birthday_place.setText(f"{date1}, {self.lnEdit_performer_birthplace.text()}")
            self.lnEdit_performer_name.setText(API_Actors.get_actor_data(api_data, 'name')[0])
            self.lnEdit_performer_nationality.setText(API_Actors.get_actor_extras(api_data, 'nationality'))
            self.txtEdit_performer_tattoo.setPlainText(API_Actors.get_actor_extras(api_data, 'tattoos'))
            self.lnEdit_performer_height.setText(f"{API_Actors.get_actor_extras(api_data, 'height')}")
            self.lnEdit_performer_boobs.setText(API_Actors.get_actor_extras(api_data, 'cupsize'))
            self.chkBox_fake_boobs.setChecked(API_Actors.get_actor_extras(api_data, 'fake_boobs'))                                
            self.txtEdit_performer_piercing.setPlainText(API_Actors.get_actor_extras(api_data, 'piercings'))
            self.lnEdit_performer_weight.setText(f"{API_Actors.get_actor_extras(api_data, 'weight')}")        
            self.lnEdit_performer_measurements.setText(API_Actors.get_actor_extras(api_data, 'measurements'))
            self.lnEdit_performer_career_start_year.setText(f"{API_Actors.get_actor_extras(api_data, 'career_start_year')}")
            self.lnEdit_performer_career_end_year.setText(f"{API_Actors.get_actor_extras(api_data, 'career_end_year')}") 

            self.set_actor.set_aliases_in_lineedit(API_Actors.get_actor_extras(api_data, 'aliases'))
            self.set_actor.set_medialink_in_table(API_Actors.get_actor_extras(api_data, 'links'))
            self.set_actor.set_medialink_from_mydb_in_table()
            self.set_actor.set_actor_site_performers(API_Actors.get_actor_data(api_data, 'site_performers')[0])

            no_image = False
            if self.Main.tblWdg_performer_links.findItems("https://cdn.theporndb.net/performer/", Qt.MatchFlag.MatchContains): 
                no_image = True   
            data, number = API_Actors.get_actor_image(api_data, 'posters', no_image, self.image_counter)

            self.lbl_image_max.setText(f"Maximale Anzahl Bilder: {self.image_counter} von Max: {number}")
            if data is not None:
                self.set_actor.set_actor_image_in_label(data)

            self.set_actor.set_actor_in_combobox(API_Actors.get_actor_extras(api_data, 'ethnicity'), widget='rasse')
            self.set_actor.set_actor_in_combobox(API_Actors.get_actor_extras(api_data, 'eye_colour'), widget='eye')
            self.set_actor.set_actor_in_combobox(API_Actors.get_actor_extras(api_data, 'hair_colour'), widget='hair')
            

    def add_item_in_mydb_table(self):
        row_index = self.tblWdg_actor_medialinks_from_mydb.rowCount()
        self.tblWdg_actor_medialinks_from_mydb.insertRow(row_index)
    
    def del_item_in_mydb_table(self):
        current_row = self.tblWdg_actor_medialinks_from_mydb.currentRow()
        self.tblWdg_actor_medialinks_from_mydb.removeRow(current_row)

    def show_last_log(self):
        showdialog = ShowLogDialogThePornDB(self)        
        showdialog.exec()    

    ### ----------------------- Search tabelle ----------------------------------- ###
    def get_search_result_header(self) -> list:
        return ["UUID","Name"]
    def set_search_result_in_table(self, api_data):
        if not api_data:
            return        
        uuid, search_count = API_Actors.get_actor_data(api_data, 'id')        
        self.tblWdg_search_result_actors.setRowCount(search_count)
        header_labels = self.get_search_result_header()
        self.tblWdg_search_result_actors.setColumnCount(len(header_labels))
        self.tblWdg_search_result_actors.setHorizontalHeaderLabels(header_labels)
        for zeile in range(search_count):
            data = api_data['data'][zeile]             
            self.tblWdg_search_result_actors.setItem(zeile, 0, QTableWidgetItem(f"{data.get('id')}"))
            self.tblWdg_search_result_actors.setItem(zeile, 1, QTableWidgetItem(f"{data.get('name')}"))

    def onItemClicked(self, index: QModelIndex) -> None:        
        uuid = self.tblWdg_search_result_actors.item(index.row(), 0).text()
        if not uuid:
            return
        self.clear_all_fields()
        self.api_link = f"https://api.theporndb.net/performers/{uuid}"        
        self.lnEdit_performer_uuid.setText(uuid)        
        self.search = False
        if self.apiThread is not None and self.apiThread.isRunning():
            # Der Thread läuft bereits, daher stoppen wir ihn
            self.apiThread.quit()
            self.apiThread.wait()
        self.apiThread = ScrapeAPIThePornDBThread(self.api_link)          
        self.apiThread.start()        

    ### --------------------------- get informations von Main -------------------------------- ###
    def get_medialinks_from_mydb(self) -> dict:
        medialinks = {}        
        biosites = self.Main.get_bio_websites(True)
        for biosite in biosites[:1] + biosites[2:]: # skip "theporndb"
            bio_widget = getattr(self.Main, f"Btn_performer_in_{biosite}")
            if bio_widget.toolTip():
                medialinks[biosite] = bio_widget.toolTip()
        return medialinks
    
    def get_socialmedia_from_mydb(self, socialmedia: dict) -> dict:
        socialmedias = GetLabels().get_avaible_socialmedia_buttons(self.Main,"Btn_performers_socialmedia_")
        for index in range(socialmedias): 
            bio_widget = getattr(self.Main, f"Btn_performers_socialmedia_{index}")
            if bio_widget.toolTip():
                name = self.set_actor.get_socialmedia_name_from_link(bio_widget.toolTip())
                socialmedia[name] = bio_widget.toolTip()
        return socialmedia
    
    def get_iafd_from_mydb(self, medialinks: dict) -> dict:
        if self.Main.lnEdit_DBIAFD_artistLink.text():
            medialinks["IAFD"] = self.Main.lnEdit_DBIAFD_artistLink.text()
        return medialinks
    
    def clear_all_fields(self):
        for txt_edit in ['tattoo', 'piercing']:
            getattr(self, f"txtEdit_performer_{txt_edit}").clear()
        for line_edit in ['name', 'uuid', 'id', 'height', 'nationality', 'birthplace', 'birthday', 'boobs', 'weight', 'measurements', 'aliases']:
            getattr(self, f"lnEdit_performer_{line_edit}").clear()
        for combobox in ['eye', 'rasse', 'hair']:
            getattr(self, f"cBox_performer_{combobox}").setCurrentIndex(-1)
        for label in ['birthday_place']:
            getattr(self, f"lbl_actor_{label}").clear()
        # for child in self.scrollArea_actor_images.findChildren(QLabel):
        #     child.clear()
        # for i in range(self.image_counter):
        #     if hasattr(self, f"lbl_image{i}"):
        #         label = getattr(self, f"lbl_image{i}")
        #         del label
        
        for widget_table in ['api', 'mydb']:
            getattr(self, f"tblWdg_actor_medialinks_from_{widget_table}").clearContents()
        self.tblWgd_arctor_links.clearContents()

        
           

if __name__ == '__main__':
    ScrapeActorInfos(QDialog)
     