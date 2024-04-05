from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QScrollArea, QHBoxLayout, QWidget, QLabel, QTableWidgetItem
from PyQt6.QtGui import QIcon, QPixmap, QMovie
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer, QModelIndex

from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper
from utils.web_scapings.theporndb.api_prepare_for_gui import API_Actors
from utils.web_scapings.theporndb.upload_performer_in_theporndb import UploadPerformer
from gui.helpers.message_show import MsgBox

from datetime import datetime
import json

from config import SRACPE_ACTOR_INFOS_UI, EINSTELLUNGEN_JSON_PATH


class WorkerThread(QThread):
    resultReady = pyqtSignal(object)
    def __init__(self, api_link, parent: str=None) -> None: 
        super().__init__(parent)
        self.api_link = api_link

    def run(self):        
        api_data = TPDB_Scraper.get_tpdb_data(self.api_link)
        self.resultReady.emit(api_data)

class ScrapeActorInfos(QDialog):
    def __init__(self, api_link, parent): # von wo es kommt  
        super(ScrapeActorInfos, self).__init__(parent)
        self.Main = parent   
        self.search = False 
        self.api_link = api_link        
        if not api_link.startswith('https://api.theporndb.net/'):
            self.search = True
            self.api_link = f"https://api.theporndb.net/performers?q={api_link}"

        uic.loadUi(SRACPE_ACTOR_INFOS_UI, self)
        self.uploader = UploadPerformer(self.Main, self)        
        self.set_progress_gif()
        self.thread = None  # Initialize thread attribute
        self.tblWdg_search_result_actors.itemClicked.connect(self.onItemClicked)
        self.Btn_get_DB_data_in_dialog.clicked.connect(self.get_DB_data_in_dialog)
        self.Btn_set_DB_data_in_dialog.clicked.connect(self.set_DB_data_in_dialog)
        self.Btn_upload_datas.clicked.connect(self.uploader.upload_performer)
                
    def set_progress_gif(self):
        self.movie = QMovie(":/Buttons/_labels/loading_progress.gif")        
        self.lbl_loading_progress.setMovie(self.movie)   
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gif)
        self.timer.start(100) # alle 100ms

    def update_gif(self):
        # GIF Animation um 1 Frame weiter
        self.lbl_loading_progress.movie().jumpToNextFrame()
        
    def showEvent(self, event):
        self.start_thread()

    def start_thread(self):
        self.thread = WorkerThread(self.api_link)
        self.thread.resultReady.connect(self.onResultReady)        
        self.thread.start()  

    def closeEvent(self, event):
        self.thread.quit() 
        self.thread.wait()
        super().closeEvent(event)

    def onResultReady(self, api_data):
        self.get_api_actors_infos(api_data)

    def get_api_actors_infos(self, api_data):                
        #api_data = TPDB_Scraper.get_tpdb_data(self.api_link)
        if api_data.get('message') == 'Unauthenticated.':
            MsgBox(self.Main, "'Unauthenticated' Du bist nicht angemeldet. Bitte melde dich an.","w")
            self.reject() 
            return
        elif api_data.get('message') == 'key missing':
            MsgBox(self.Main, "kein API Key vorhanden. Setze einen in den Einstellungen !","w")
            self.reject()
            return
        elif api_data.get('data') == []:
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
                lnEdit.setText(getattr(self.Main, f"lnEdit_performer_{lineedit}").text())
                lnEdit.setStyleSheet("background-color: #FFFDD5;")                
        for textedit in text:
            txtEdit = getattr(self, f"txtEdit_performer_{textedit}")
            if txtEdit.activated:
                txtEdit.setPlainText(getattr(self.Main, f"txtBrw_performer_{textedit}").toPlainText())
                txtEdit.setStyleSheet("background-color: #FFFDD5;")               

    def set_DB_data_in_dialog(self):
        line, text = self.get_all_widgets()
        for lineedit in line:
            lnEdit_main = getattr(self.Main, f"lnEdit_performer_{lineedit}")
            lnEdit = getattr(self, f"lnEdit_performer_{lineedit}")
            if lnEdit.activated:
                lnEdit_main.setText(lnEdit.text())
                lnEdit.setStyleSheet("background-color: #FFFDD5;")                
        for textedit in text:
            txtEdit_main = getattr(self.Main, f"txtEdit_performer_{textedit}")
            txtEdit = getattr(self, f"txtEdit_performer_{textedit}")
            if txtEdit.activated:
                txtEdit_main.setPlainText(txtEdit.toPlainText())
                txtEdit.setStyleSheet("background-color: #FFFDD5;")                
        #### ----------------- set api link in Button --------------------- ####
        uuid = self.lnEdit_performer_uuid.text()
        if uuid:
            self.Main.Btn_performer_in_theporndb.setToolTip(f"https://api.theporndb.net/performers/{uuid}")
            self.lnEdit_performer_uuid.setStyleSheet("background-color: #FFFDD5;")
            self.lnEdit_performer_uuid.activated = False
            self.check_avaible_bio_websites() 

    def check_avaible_bio_websites(self):
        widget = self.Main.get_bio_websites(widget=True)[1]
        icon = QIcon()
        icon.addPixmap(QPixmap(f":/Buttons/_buttons/performer_biosites/{widget}.png"), QIcon.Mode.Normal, QIcon.State.Off)
        bio_button = getattr(self.Main, f"Btn_performer_in_{widget}")
        bio_button.setIcon(icon)
        bio_button.setIconSize(QSize(50, 25))
        self.Main.Btn_DBArtist_Update.setEnabled(True) 

    def get_all_widgets(self):
        lineedits = ["hair", "birthplace", "birthday", "eye", "boobs", "height", "weight"]
        textedit = ["piercing", "tattoo"]
        return lineedits, textedit

    def set_api_infos_ui(self, api_data):                
        uuid, search_count = API_Actors.get_actor_data(api_data, 'id')
        self.lnEdit_performer_uuid.setText(uuid)
        if self.search and search_count >0:
            self.lbl_search_counter.setText(f"gefundene Personen: {search_count}") 
            self.set_search_result_in_table(api_data)
            self.timer.stop()                        
        else:
            image_counter = self.get_image_counter()            
            self.set_gender_icon(API_Actors.get_actor_extras(api_data, 'gender'))
            date1, date2 = self.date_formarted(API_Actors.get_actor_extras(api_data,'birthday'))                   
            self.lnEdit_performer_birthday.setText(date2)            
            self.lnEdit_performer_birthplace.setText(API_Actors.get_actor_extras(api_data, 'birthplace'))
            self.lbl_actor_birthday_place.setText(f"{date1}, {self.lnEdit_performer_birthplace.text()}")
            self.lnEdit_performer_name.setText(API_Actors.get_actor_data(api_data, 'name')[0])
            self.lnEdit_performer_nationality.setText(API_Actors.get_actor_extras(api_data, 'nationality'))
            self.txtEdit_performer_tattoo.setPlainText(API_Actors.get_actor_extras(api_data, 'tattoos'))
            self.lnEdit_performer_height.setText(API_Actors.get_actor_extras(api_data, 'height'))
            self.lnEdit_performer_boobs.setText(API_Actors.get_actor_extras(api_data, 'cupsize'))
            self.lnEdit_performer_hair.setText(API_Actors.get_actor_extras(api_data, 'hair_colour'))
            self.lnEdit_performer_eye.setText(API_Actors.get_actor_extras(api_data, 'eye_colour'))        
            self.txtEdit_performer_piercing.setPlainText(API_Actors.get_actor_extras(api_data, 'piercings'))
            self.lnEdit_performer_weight.setText(API_Actors.get_actor_extras(api_data, 'weight'))        
            self.lnEdit_performer_meaturements.setText(API_Actors.get_actor_extras(api_data, 'measurements')) 

            self.set_aliases_in_lineedit(API_Actors.get_actor_extras(api_data, 'aliases'))
            self.set_medialink_in_table(API_Actors.get_actor_extras(api_data, 'links'))
            self.set_actor_site_performers(API_Actors.get_actor_data(api_data, 'site_performers')[0])

            data, number=API_Actors.get_actor_image(api_data, 'posters', image_counter)
            self.lbl_image_max.setText(f"Maximale Anzahl Bilder: {image_counter} von Max: {number}")
            self.set_actor_image_in_label(data)

            self.set_actor_ethnicity_in_combobox(API_Actors.get_actor_extras(api_data, 'ethnicity'))
            self.timer.stop()            
    def set_aliases_in_lineedit(self, aliases: list) -> None:
        if not aliases:
            return
        self.lnEdit_performer_aliases.setText(', '.join(aliases[0]))

    def get_image_counter(self):
        set = json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes()) 
        image_counter = set["tpdb_image_counter"]
        return image_counter

    def set_gender_icon(self, gender: str) -> None:
        if not gender:
            return
        size = QSize(25, 30)
        if gender =='Female':
            icon = QIcon(":Buttons\_buttons\gender\person-weiblich.png")
            pixmap = icon.pixmap(size)            
            self.lbl_actor_gender_sign.setPixmap(pixmap) 
            self.lbl_actor_gender_sign.setProperty("gender", "female")
        elif gender == 'Male':
            icon = QIcon(":Buttons\_buttons\gender\person-maennlich.png")
            pixmap = icon.pixmap(size) 
            self.lbl_actor_gender_sign.setPixmap(pixmap)            
            self.lbl_actor_gender_sign.setProperty("gender", "male")
        else:
            icon = QIcon(":Buttons\_buttons\gender\person-trans.png")
            pixmap = icon.pixmap(size)
            self.lbl_actor_gender_sign.setPixmap(pixmap)
            pixmap = icon.pixmap() 
            self.lbl_actor_gender_sign.setProperty("gender", "trans")

    def date_formarted(self, date: str) -> str:
        if not date:
            return "",""
        date = datetime.strptime(date, "%Y-%m-%d").date()
        format1 = date.strftime("%d %b., %Y") # Format 1: 10 Jan., 1992      
        format2 = date.strftime("%d.%m.%Y") # Format 2: 10.01.1992 
        return format1, format2

    def set_actor_ethnicity_in_combobox(self, ethnicity: str) -> None:
        if not ethnicity:
            self.cBox_performer_rasse.setCurrentIndex(0)
            return        
        index = self.cBox_performer_rasse.findText(ethnicity)
        if index >= 0: 
            self.cBox_performer_rasse.setCurrentIndex(index)

    def set_actor_site_performers(self, site_performers: list) -> None:
        if not site_performers:
            return 
        site_extra = []
        self.tblWgd_arctor_links.setRowCount(len(site_performers))
        header_labels = self.get_site_extras()  
        self.tblWgd_arctor_links.setColumnCount(len(header_labels))
        self.tblWgd_arctor_links.setHorizontalHeaderLabels(header_labels)
        for zeile, name in enumerate(site_performers): 
            site_name = name['site'].get('name')
            name_on_site = name.get('name')            
            self.tblWgd_arctor_links.setItem(zeile, 0, QTableWidgetItem(f'{site_name}'))
            self.tblWgd_arctor_links.setItem(zeile, 1, QTableWidgetItem(f'{name_on_site}'))
            for idx, extra in enumerate(header_labels[2:]):
                a = name['parent']
                site_extra = name['parent']['extras'].get(extra)
                self.tblWgd_arctor_links.setItem(zeile, idx+2, QTableWidgetItem(f'{site_extra}'))
        self.tblWgd_arctor_links.setCurrentCell(0, 0)

    def set_medialink_in_table(self, medialinks: list) -> None:
        if not medialinks:
            return
        header_labels = medialinks.keys()
        self.tblWdg_actor_medialinks.setRowCount(len(medialinks))
        self.tblWdg_actor_medialinks.setColumnCount(len(header_labels))
        self.tblWdg_actor_medialinks.setHorizontalHeaderLabels(header_labels)
        for zeile, (media_name, media_link) in enumerate(medialinks.items()):            
            self.tblWdg_actor_medialinks.setItem(zeile, 0, QTableWidgetItem(f'{media_name}'))
            self.tblWdg_actor_medialinks.setItem(zeile, 0, QTableWidgetItem(f'{media_name}'))
            
    def get_site_extras(self) -> list:
        return ["Site-Name","Name", "birthplace", "ethnicity", "eye_colour", "haircolor", "fakeboobs", "gender",
                "height", "measurements", "nationality", "piercings", "tattoos", "weight"]

    def set_actor_image_in_label(self, image_datas: list) -> None:
        if not image_datas:
            return
        elif image_datas == "403":
            self.lbl_scene_image.setStyleSheet('background-image:url(:/label/labels/403 Forbidden.jpg);')
            return
        self.lbl_image_counter.setText(f"{len(image_datas)} Bilder")
        scroll_area = self.findChild(QScrollArea, "scrollArea_actor_images")
        # QVBoxLayout für das QScrollArea-Widget erstellen
        layout = QHBoxLayout()        
        for idx, image_data in enumerate(image_datas):            
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            scaled_pixmap = pixmap.scaled(170, 256, Qt.AspectRatioMode.KeepAspectRatio)
            label = QLabel()
            label.setPixmap(scaled_pixmap)
            layout.addWidget(label) 
        widget = QWidget()
        widget.setLayout(layout)
        # Größe des Widget an die Anzahl der Bilder anpassen
        widget.setFixedSize(widget.sizeHint())
        # QScrollArea-Widget das Layout setzen
        scroll_area.setWidget(widget)

    ### ----------------------- Seatch tabelle ----------------------------------- ###

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
        self.lnEdit_performer_uuid.setText(uuid)       
        self.api_link = f"https://api.theporndb.net/performers/{uuid}"
        self.thread = None
        self.search = False
        self.start_thread()
    

        
           

if __name__ == '__main__':
    ScrapeActorInfos(QDialog)
     