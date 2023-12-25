from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt, QTimer, QCoreApplication
from PyQt6.QtGui import QPixmap, QIcon, QColor, QBrush

import json
from pathlib import Path 
from typing import Tuple
from urllib.parse import urlparse
import time
import logging

from utils.web_scapings.websides import Infos_WebSides
from utils.database_settings.database_for_darsteller import DB_Darsteller
from utils.web_scapings.iafd_performer_link import IAFDInfos
from gui.dialoge_ui.message_show import StatusBar, blink_label, MsgBox

from config import PROJECT_PATH, RASSE_JSON

class PerformerInfosMaske():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow  
        logging.basicConfig(filename='log_updates.log', level=logging.INFO, 
            format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')      

    def artist_infos_in_maske(self):
        self.Main.set_performer_maske_text_connect(disconnect=True) 
        self.clear_maske()
        iafd_infos=IAFDInfos(MainWindow=self.Main)
        infos_webside=Infos_WebSides(MainWindow=self.Main)
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        time.sleep(.1)
        selected_items = self.Main.tblWdg_performer.selectedItems()
        ### --------- Name Überschrift setzen ------------------------- ###
        self.Main.grpBox_performer.setTitle(f"Performer-Info ID: {selected_items[0].text()}")         
        self.Main.lnEdit_performer_info.setText(selected_items[1].text().strip()) # Name
        self.Main.lnEdit_performer_ordner.setText(selected_items[2].text().strip()) # Ordner
        ### --------- Geschlechts QComboBox setzen -------------------- ### 
        sex_dict = {"0": "", "1": "weiblich","2": "männlich","3": "transsexuell"}  
        sex=""
        try:      
            sex = sex_dict.get(selected_items[5].text(),"0")   # "0" ergibt ein Text von ""
        except IndexError as e:
            print(f"artist_infos_in_maske(sex): {e} -> {selected_items[0].text()} Name: {selected_items[1].text()}")
        self.Main.cBox_performer_sex.setCurrentText(sex)
        infos_webside.set_tooltip_text("cBox_performer_", "sex", f"Datenbank: {sex}", "Datenbank")
        ### --------- Rasse QComboBox setzen ------------------------- ### 
        rasse_dict = json.loads(RASSE_JSON.read_bytes())
        rasse=""
        try:
            rasse = rasse_dict["zahl_rasse"].get(selected_items[6].text(),"")  # "" ergibt als Text "0" -> "rasse_zahl": {"": "0", .... 
        except IndexError as e:
            print(f"artist_infos_in_maske(rasse): {e} -> {selected_items[0].text()} Name: {selected_items[1].text()}")     
        self.Main.cBox_performer_rasse.setCurrentText(rasse)       
        infos_webside.set_tooltip_text("cBox_performer_", "rasse", f"Datenbank: {rasse}", "Datenbank")
        ### --------- Nation QComboBox setzen -- von englisch(DB) in deutsch(Maske) ------ ###        
        nations=selected_items[7].text().split(", ")        
        for nation_ger in nations: 
            if self.Main.cBox_performer_nation.findText(nation_ger, flags=Qt.MatchFlag.MatchExactly) == -1 and nation_ger: 
                self.Main.cBox_performer_nation.addItem(nation_ger)           
        infos_webside.set_tooltip_text("cBox_performer_", "nation", f"Datenbank: {nation_ger}", "Datenbank")
        ### --------- Fan Side/OnlyFans QComboBox setzen -------------- ###
        for fan_side in selected_items[10].text().split("\n"):
            if self.Main.cBox_performer_fanside.findText(fan_side, flags=Qt.MatchFlag.MatchExactly) == -1 and fan_side:            
                self.Main.cBox_performer_fanside.addItem(fan_side)        
        infos_webside.set_tooltip_text("cBox_performer_", "fanside", f"Datenbank: {fan_side}", "Datenbank")
        ### --------- Quell Links in QTableWidget setzen -------------- ### 
        self.update_names_linksatz_in_ui(selected_items[0].text())  
        ### --------- IAFD Link setzen -------------------------------- ### 
        if selected_items[3].text():            
            if selected_items[3].text()=="N/A":
                self.Main.chkBox_iafd_enabled.setChecked(False) # IAFD feld deaktivieren                              
                self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(False)
            else:
                self.Main.chkBox_iafd_enabled.setChecked(True)
                self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)
                self.Main.lbl_checkWeb_IAFD_artistURL.setStyleSheet("background-image: url(':/labels/_labels/check.png')")
            infos_webside.set_daten_in_maske("lnEdit_DB", "IAFD_artistLink", "Datenbank", selected_items[3].text(), artist=True)
        elif self.Main.chkBox_get_autom_iafd.isChecked():
             self.Main.lnEdit_create_iafd_link.setText(selected_items[1].text())                      
             iafd_infos.get_IAFD_performer_link() 
             self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)         
        ### --------- BabePedia Link setzen -------------------------------- ###
        if selected_items[4].text():                     
            infos_webside.set_daten_in_maske("lnEdit_DB", "BioWebsite_artistLink", "Datenbank", selected_items[4].text(), artist=True)              
            self.Main.Btn_performer_in_BabePedia.setEnabled(True)
            self.Main.lbl_checkWeb_BabePedia_artistURL.setStyleSheet("background-image: url(':/labels/_labels/check.png')")
        ### ----------- Rest in Maske packen ------------ ###        
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "geburtstag", "Datenbank", selected_items[8].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "geburtsort", "Datenbank", selected_items[9].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "boobs", "Datenbank", selected_items[11].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "gewicht", "Datenbank", selected_items[12].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "groesse", "Datenbank", selected_items[13].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "bodytyp", "Datenbank", selected_items[14].text(),artist=True)
        infos_webside.set_daten_with_tooltip("txtEdit_performer_", "piercing", "Datenbank", selected_items[15].text(),artist=True)
        infos_webside.set_daten_with_tooltip("txtEdit_performer_", "tattoo", "Datenbank", selected_items[16].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "haar", "Datenbank", selected_items[17].text(), artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "augen", "Datenbank", selected_items[18].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "aktiv", "Datenbank", selected_items[19].text(),artist=True)        
        ### ----------- IAFD Image in Label setzen ------- ###
        errview, image_pfad = datenbank_darsteller.get_iafd_image(selected_items[0].text())
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            infos_webside.set_tooltip_text("lbl_", "iafd_image", f"Datenbank: '{image_pfad}'", "Datenbank")
            pixmap = QPixmap()
            pixmap.load(str(image_pfad))
            self.Main.stacked_webdb_images.setCurrentWidget(self.Main.stacked_iafd_label)
        else:
            infos_webside.set_tooltip_text("lbl_", "iafd_image", f"Datenbank: 'Kein Bild gespeichert'", "Datenbank")                              
            pixmap = QPixmap(":/labels/_labels/kein-bild.jpg")                   
        self.Main.lbl_iafd_image.setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))        
        ### ----------- BabePedia Image in Label setzen ------- ###
        errview, image_pfad = datenbank_darsteller.get_babepedia_image(selected_items[0].text())
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            infos_webside.set_tooltip_text("lbl_", "babepedia_image", f"Datenbank: '{image_pfad}'", "Datenbank")
            pixmap = QPixmap()
            pixmap.load(str(image_pfad))
            self.Main.stacked_webdb_images.setCurrentWidget(self.Main.stacked_babepedia_label)
        else:
            infos_webside.set_tooltip_text("lbl_", "babepedia_image", f"Datenbank: 'Kein Bild gespeichert'", "Datenbank")                              
            pixmap = QPixmap(":/labels/_labels/kein-bild.jpg")                   
        self.Main.lbl_babepedia_image.setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))
        self.Main.set_performer_maske_text_connect(disconnect=False)         


    def get_artistdata_from_ui(self, database: bool=False) -> Tuple[dict, list]:
        ### -------------- Geschlecht für update vorbereiten ------------------ ###
        sex_dict = {"": "0", "weiblich": "1", "männlich": "2","transsexuell": "3"}
        sex = sex_dict.get(self.Main.cBox_performer_sex.currentText())
        ### -------------- RassenID für update vorbereiten -------------------- ###        
        rasse_dict = json.loads(RASSE_JSON.read_bytes())
        rassen_id=rasse_dict["rasse_zahl"].get(self.Main.cBox_performer_rasse.currentText(),"")
        ### -------------- Nation für update vorbereiten ----------------------- ### 
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main) 
        artist_id=int(self.Main.grpBox_performer.title().replace("Performer-Info ID: ",""))
        nation_message: str=""
        nations_list: list=[]
        for i in range(self.Main.cBox_performer_nation.count()):  # combobox.allItems()
            nations_list.append(self.Main.cBox_performer_nation.itemText(i)) 
        nations=", ".join(nations_list)                  
        errview, is_addet = datenbank_darsteller.add_nations_person(nations, artist_id)
        if errview and not "Nation: None nicht in der Datenbank !":
            nation_message=f". Fehler beim Nation Adden: {errview}" 
        elif is_addet:
            nation_message=". Eine Nation wurde geaddet"           
         ### -------------- Only Fans für update vorbereiten ------------------- ### 
        only_fans=""        
        for index in range(self.Main.cBox_performer_fanside.count()):
            item_text = self.Main.cBox_performer_fanside.itemText(index)
            only_fans+=item_text+"\n"
        if only_fans is not None:
            only_fans=only_fans[:-1]
        daten_satz = {
            "ArtistID" : artist_id,
            "Name": self.Main.lnEdit_performer_info.text(),
            "Ordner": self.Main.lnEdit_performer_ordner.text(),
            "IAFDLink": self.Main.lnEdit_DBIAFD_artistLink.text(),
            "BabePedia": self.Main.lnEdit_DBBioWebsite_artistLink.text(),
            "Geschlecht": sex,            
            "RassenID": rassen_id,
            "Nation": nations,            
            "Geburtstag": self.Main.lnEdit_performer_geburtstag.text(),
            "Birth_Place": self.Main.lnEdit_performer_geburtsort.text(),
            "OnlyFans": only_fans,
            "Boobs": self.Main.lnEdit_performer_boobs.text(),
            "Gewicht": self.Main.lnEdit_performer_gewicht.text().replace(" kg",""),
            "Groesse": self.Main.lnEdit_performer_groesse.text().replace(" cm",""),
            "Bodytyp": self.Main.lnEdit_performer_bodytyp.text(),
            "Piercing": self.Main.txtEdit_performer_piercing.toPlainText(),
            "Tattoo": self.Main.txtEdit_performer_tattoo.toPlainText(),
            "Haarfarbe": self.Main.lnEdit_performer_haar.text(),
            "Augenfarbe": self.Main.lnEdit_performer_augen.text(),
            "Aktiv": self.Main.lnEdit_performer_aktiv.text(),                                       
                    }
        names_link_satz = []
        if database:            
            names_link_satz=self.nameslink_datensatz_in_dict(names_link_satz)
        return daten_satz, names_link_satz, nation_message
    
    def nameslink_datensatz_in_dict(self, names_link_satz):
        for zeile in range(self.Main.tblWdg_performer_links.rowCount()):
            pfad = self.file_rename_and_move(zeile)
            link = self.Main.tblWdg_performer_links.item(zeile, 1).text()
            alias = self.Main.tblWdg_performer_links.item(zeile, 3).text()
            alias = self.Main.lnEdit_IAFD_artistAlias.text() if link.startswith("https://www.iafd.com/person.rme/perfid=") and not alias else alias   
            names_id_str = self.Main.tblWdg_performer_links.item(zeile, 0).text()            
            row_data = {
                "NamesID": int(names_id_str) if names_id_str is not None and names_id_str.isdigit() else -1,
                "Link": link,
                "Image": pfad,
                "Alias": alias  }
            names_link_satz.append(row_data)
        return names_link_satz

    def file_rename_and_move(self, zeile: int) -> str:
        pfad=self.Main.tblWdg_performer_links.item(zeile, 2).text()
        ordner = self.Main.lnEdit_performer_ordner.text()
        if pfad:
            path_part=pfad.replace("__artists_Images/","")                         
            pfad_neu = pfad.replace(path_part[:path_part.find("/")],ordner)
            if pfad_neu!=pfad:
                if not Path(PROJECT_PATH / "__artists_Images" / ordner).exists(): # makedir, wenn keins da
                    Path(PROJECT_PATH / "__artists_Images" / ordner).mkdir()
                old_path = Path(PROJECT_PATH / pfad)
                new_path = PROJECT_PATH / pfad_neu
                try:
                    old_path.rename(new_path) # verschiebt und renamed zugleich
                except  FileNotFoundError as e:
                    StatusBar(self.Main, f"Error bei: {old_path} mit {e}", "#ff0000")
                else:
                    pfad=pfad_neu
                    if old_path.is_dir() and not any(old_path.iterdir()): # altes Verzeichnis löschen, wenn es leer ist                    
                        old_path.rmdir()
        return pfad
    
    def update_names_linksatz_in_ui(self, artist_id: int):
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        nameslink_datensatz = datenbank_darsteller.get_quell_links(artist_id) #ArtistID -> DB_NamesLink.NamesID
        for zeile, (id, link, image, alias) in enumerate(zip(*nameslink_datensatz)):                   
            self.Main.tblWdg_performer_links.setRowCount(zeile+1)
            self.Main.tblWdg_performer_links.setItem(zeile,0,QTableWidgetItem(f"{id}"))            
            self.Main.tblWdg_performer_links.setItem(zeile,1,QTableWidgetItem(link))
            self.Main.tblWdg_performer_links.setItem(zeile,2,QTableWidgetItem(image))
            self.Main.tblWdg_performer_links.setItem(zeile,3,QTableWidgetItem(alias))
            self.set_icon_in_tablewidget(zeile, image)
            self.setColortoRow(self.Main.tblWdg_performer_links,zeile,'#FFFDD5')
            if link.startswith("https://www.iafd.com/person.rme/perfid="):
                self.Main.lnEdit_IAFD_artistAlias.setText(alias)                                           
        self.Main.tblWdg_performer_links.update()
        self.Main.tblWdg_performer_links.resizeColumnsToContents()

    def set_icon_in_tablewidget(self, zeile, image):
        item = QTableWidgetItem() 
        if image and Path(PROJECT_PATH / image).exists():                
            item.setIcon(QIcon(':/labels/_labels/check.png'))  
        else:
            item.setIcon(QIcon(':/labels/_labels/error.png'))
        self.Main.tblWdg_performer_links.setItem(zeile,4,item)
    
    def put_daten_satz_in_tablewidget(self): 
        daten_satz,_,_ = self.get_artistdata_from_ui()
        artist_id=daten_satz["ArtistID"]
        for zeile in range(self.Main.tblWdg_performer.rowCount()):
            item = self.Main.tblWdg_performer.item(zeile, 0)
            if item is not None and str(artist_id) in item.text():                
                for spalte, (key, value) in enumerate(daten_satz.items()):
                    self.Main.tblWdg_performer.setItem(zeile, spalte, QTableWidgetItem(str(value)))
                    self.Main.tblWdg_performer.update()
                    self.Main.tblWdg_performer.selectRow(zeile)
                return artist_id, zeile+1  
        return 0, 0        

    def update_datensatz(self):
        self.Main.Btn_DBArtist_Update.setEnabled(False)         
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)        
        nameslink_msg: str=""
        is_neu_datensatz: int=0 
        is_update_datensatz: int=0  
        #### --------------- IAFD Image und andere Images werden gespeichert ----------------------------- ####
        iafd_message = self.save_iafd_image_in_datenbank()        
        #### -------------------------------------------------------------- ####     
        artist_id, zeile= self.put_daten_satz_in_tablewidget()
        daten_satz, names_link_satz, nation_message=self.get_artistdata_from_ui(database=True)                 
        artist_id = daten_satz["ArtistID"]
        ### ------------ Update was in der Tabelle von Performer_Links drin ist --------------- ###
        for linksatz in names_link_satz:
            url=linksatz["Link"]
            studio_link = f"{urlparse(url).scheme}://{urlparse(url).netloc}/"                       
            studio_id = datenbank_darsteller.get_studio_id_from_baselink(studio_link)
            if studio_id > -1:                                
                datensatz_list = datenbank_darsteller.get_nameslink_dataset_from_namesid(linksatz["NamesID"])
                linksatz_list = list(linksatz.values())
                if datensatz_list and linksatz_list != datensatz_list:                    
                    is_update_datensatz += datenbank_darsteller.update_performer_names_link(artist_id, linksatz, studio_id)
                elif not datensatz_list:
                    is_neu_datensatz_db, _ = datenbank_darsteller.add_db_artistlink(artist_id, linksatz, studio_id)  
                    is_neu_datensatz += is_neu_datensatz_db
            else:
                StatusBar(self.Main, f"keine Studio ID für {studio_link} gefunden, kein update, add möglich !","#FF0000")
        ### --------------- Anzeige was alles neu, updated ist und refresh tabelle -------------------- ###         
        if (is_neu_datensatz or is_update_datensatz) > 0:
            self.update_names_linksatz_in_ui(daten_satz["ArtistID"])
            nameslink_msg="NamesLink"
        ### ------------ Update alles was oben in der Maske drin ist --------------- ###        
        errview, is_update= datenbank_darsteller.update_performer_datensatz(daten_satz)
        datensatz_message=""
        if not errview and is_update: # check Maske wurde updated
            datensatz_message=f"Datensatz und"
            widgets = self.Main.performers_tab_widgets()
            for widget in widgets: # masken farbe wieder bereinigen bei erfolgreichen update
                self.Main.set_color_stylesheet(widget, color_hex='#FFFDD5') 
        #### --------------------------------------------------------------- ####        
        if not errview and is_update:
            message=f"Datensatz: {artist_id} in Zeile: {zeile} wurde {datensatz_message} {nameslink_msg} updatet{iafd_message} !"
            self.Main.txtBrowser_loginfos.append(message)
            blink_label(self.Main, "lbl_db_status", "#74DF00") 
            logging.info(message)
        else:
            message=f"Datensatz: {artist_id} in Zeile: {zeile} wurde nicht updatet. Fehler: {errview}"
            blink_label(self.Main, "lbl_db_status", "#FF0000")  
        self.Main.lbl_db_status.setText(message+nation_message)

    def update_tabelle(self):
        iafd: int=0
        bio_infos: int=0        
        current_iafd: int=1
        now_iafd: int=1
        now_bio: int=1
        table_performer_count = self.Main.tblWdg_performer.rowCount()
        self.Main.stacked_image_infos.setCurrentWidget(self.Main.logger_infos)
        for zeile in range(table_performer_count):
            if self.Main.tblWdg_performer.item(zeile,3).text().startswith("https://www.iafd.com/person.rme/perfid="):
                iafd+=1
            if self.Main.tblWdg_performer.item(zeile,3).text() == "N/A":
                bio_infos+=1             
        no_infos = table_performer_count-iafd-bio_infos        
        self.Main.chkBox_get_autom_iafd.setChecked(True)
        for zeile in range(table_performer_count):            
            self.setinfo_label(now_iafd, iafd,now_bio,bio_infos,current_iafd,no_infos, table_performer_count)
            item=self.Main.tblWdg_performer.item(zeile, 0)
            item.setSelected(True)
            self.Main.tblWdg_performer.selectRow(zeile)            
            self.Main.tblWdg_performer.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
            if self.Main.tblWdg_performer.selectedItems()[3].text().startswith("https://www.iafd.com/person.rme/perfid="):
                now_iafd+=1
                continue
            elif self.Main.tblWdg_performer.selectedItems()[3].text() == "N/A":
                now_bio+=1
                continue
            current_iafd+=1
            QCoreApplication.processEvents()
            self.artist_infos_in_maske()
            iafd_infos = IAFDInfos(MainWindow=self.Main)
            iafd_infos.load_IAFD_performer_link() 
            self.save_iafd_image_in_datenbank()            
            self.update_datensatz()  
        MsgBox(self.Main,"Fertig !","i")

    def setinfo_label(self,now_iafd, iafd,now_bio,bio_infos,current_iafd,no_infos, table_performer_count):
        self.Main.lbl_infos_on_imagestacked.setText(f"IAFD: {now_iafd}|{iafd} / kein IAFDLink: {now_bio}|{bio_infos} / durchsuche: {current_iafd}|{no_infos} gesamt: {table_performer_count}")   

    def save_iafd_image_in_datenbank(self):
        iafd_message: str=""
        artist_id = int(self.Main.grpBox_performer.title().replace("Performer-Info ID: ",""))
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)        
        _,image_pfad = datenbank_darsteller.get_iafd_image(artist_id)                
        if not (image_pfad and str(Path(PROJECT_PATH / image_pfad).exists())):
            pixmap = self.Main.lbl_iafd_image.pixmap()
            if not self.is_ein_bild_dummy_im_label() and pixmap:
                name = self.Main.lnEdit_performer_info.text()                
                iafd_link=self.Main.lnEdit_DBIAFD_artistLink.text()
                try:                
                    perfid,_ = iafd_link.replace("https://www.iafd.com/person.rme/perfid=","").split("/",1)
                except ValueError:
                    print(f"ValueError: {name}: iafd_link")
                else:
                    ordner = self.Main.lnEdit_performer_ordner.text()
                    image_pfad=f"__artists_Images/{ordner}/[IAFD]-{perfid}.jpg"
                    names_link_iafd = {                        
                            "Link": iafd_link,
                            "Image": image_pfad,
                            "ArtistID": artist_id,
                            "Alias": name
                        }
                    errview, is_addet = datenbank_darsteller.add_performer_link_and_image(names_link_iafd) 
                    if is_addet:
                        iafd_message=", IAFD Bild wurde gespeichert" 
                        if not Path(Path(PROJECT_PATH / image_pfad).parent).exists():
                            Path(PROJECT_PATH / image_pfad).parent.mkdir()        
                        pixmap.save(str(PROJECT_PATH / image_pfad), "JPEG")
                        self.update_names_linksatz_in_ui(artist_id)
                    else: 
                        iafd_message=f", IAFD Bild wurde nicht gespeichert (Error: {errview})"
        return iafd_message

    def is_ein_bild_dummy_im_label(self):
        kein_bild_vorhanden_image_path = ":/labels/_labels/kein-bild.jpg" 
        kein_bild_vorhanden_image = QPixmap(str(kein_bild_vorhanden_image_path)).toImage()        
        # Lade das aktuelle Bild im Label
        current_image = self.Main.lbl_iafd_image.pixmap().toImage() if self.Main.lbl_iafd_image.pixmap() else None 
        return current_image == kein_bild_vorhanden_image # Überprüfe, ob die Bilder gleich sind
       

    def clear_maske(self):
        felder = ["sex", "rasse", "nation", "fanside", "haar", "augen", "geburtsort", "geburtstag", "boobs", "bodytyp", "aktiv", "groesse",
                "gewicht", "piercing", "tattoo"]
        self.Main.tooltip_claering(felder,artist=True)
        self.Main.lbl_iafd_image.clear()
        self.Main.lbl_iafd_image.setToolTip("")
        self.Main.lbl_babepedia_image.clear()
        self.Main.lbl_babepedia_image.setToolTip("")
        self.Main.lbl_link_image_from_db.clear()
        self.Main.lbl_link_image_from_db.setToolTip("")
        self.Main.lnEdit_IAFD_artistAlias.setText("")
        self.Main.lnEdit_IAFD_artistAlias.setToolTip("")        
        self.Main.lbl_db_status.setText("")        
        self.Main.lbl_performer_link.setText("")        
        self.Main.lnEdit_performer_ordner.setText("")
        self.Main.grpBox_performer.setTitle("Performer-Info für:")
        self.Main.lnEdit_performer_info.setText("")
        self.Main.lnEdit_DBIAFD_artistLink.setText("")
        self.Main.lnEdit_DBBioWebsite_artistLink.setText("")
        self.Main.cBox_performer_sex.setCurrentIndex(0)            
        self.Main.cBox_performer_rasse.setCurrentIndex(0)
        self.Main.cBox_performer_nation.clear()
        self.Main.lnEdit_performer_geburtstag.setText("")
        self.Main.lnEdit_performer_geburtsort.setText("")
        self.Main.cBox_performer_fanside.clear()
        self.Main.lnEdit_performer_boobs.setText("")
        self.Main.lnEdit_performer_gewicht.setText("")
        self.Main.lnEdit_performer_groesse.setText("")
        self.Main.lnEdit_performer_bodytyp.setText("")
        self.Main.txtEdit_performer_piercing.setPlainText("")
        self.Main.txtEdit_performer_tattoo.setPlainText("")
        self.Main.lnEdit_performer_haar.setText("")
        self.Main.lnEdit_performer_augen.setText("")
        self.Main.lnEdit_performer_aktiv.setText("")
        self.Main.tblWdg_performer_links.clearContents()
        self.Main.tblWdg_performer_links.setRowCount(0)

    def setColortoRow(self, table, rowIndex, color_hex):
        if color_hex=='#FFFD00':
            self.Main.Btn_DBArtist_Update.setEnabled(True)
        else:
            self.Main.Btn_DBArtist_Update.setEnabled(False)
        color = QColor(color_hex)
        brush = QBrush(color)
        for column in range(table.columnCount()-1):
            table.item(rowIndex, column).setBackground(color)

# Abschluss
if __name__ == '__main__':
    PerformerInfosMaske()