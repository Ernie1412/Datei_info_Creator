from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

import json
from pathlib import Path 
from typing import Tuple
from urllib.parse import urlparse

from utils.web_scapings.websides import Infos_WebSides
from utils.database_settings.database_for_darsteller import DB_Darsteller
from utils.web_scapings.iafd_performer_link import IAFDInfos

from config import PROJECT_PATH, RASSE_JSON

class PerformerInfosMaske():

    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow        

    def artist_infos_in_maske(self): 
        self.clear_maske()
        iafd_infos=IAFDInfos(MainWindow=self.Main)
        infos_webside=Infos_WebSides(MainWindow=self.Main)
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        ### --------- Name Überschrift setzen ------------------------- ###
        self.Main.grpBox_performer.setTitle(f"Performer-Info ID: {self.Main.tblWdg_Daten.selectedItems()[0].text()}")
        self.Main.Btn_DBArtist_Update.setEnabled(True)  
        self.Main.lnEdit_performer_info.setText(self.Main.tblWdg_Daten.selectedItems()[1].text().strip())
        ### --------- Geschlechts QComboBox setzen -------------------- ### 
        sex_dict = {"0": "", "1": "weiblich","2": "männlich","3": "transsexuell"}        
        sex = sex_dict.get(self.Main.tblWdg_Daten.selectedItems()[4].text(),"")        
        self.Main.cBox_performer_sex.setCurrentText(sex)
        infos_webside.set_tooltip_text("cBox_performer_", "sex", f"Datenbank: {sex}", "Datenbank")
        ### --------- Rasse QComboBox setzen ------------------------- ### 
        rasse_dict = json.loads(RASSE_JSON.read_bytes())
        rasse = rasse_dict["zahl_rasse"].get(self.Main.tblWdg_Daten.selectedItems()[5].text(),"")        
        self.Main.cBox_performer_rasse.setCurrentText(rasse)       
        infos_webside.set_tooltip_text("cBox_performer_", "rasse", f"Datenbank: {rasse}", "Datenbank")
        ### --------- Nation QComboBox setzen -- von englisch(DB) in deutsch(Maske) ------ ###        
        nations=self.Main.tblWdg_Daten.selectedItems()[6].text().split(", ")        
        for nation_ger in nations:  
                #nation_ger=datenbank_darsteller.get_nation_ger_to_english(nation_ger)          
                if self.Main.cBox_performer_nation.findText(nation_ger, flags=Qt.MatchFlag.MatchExactly) == -1 and nation_ger: 
                    self.Main.cBox_performer_nation.addItem(nation_ger)           
        infos_webside.set_tooltip_text("cBox_performer_", "nation", f"Datenbank: {nation_ger}", "Datenbank")
        ### --------- Fan Side/OnlyFans QComboBox setzen -------------- ###
        for fan_side in self.Main.tblWdg_Daten.selectedItems()[9].text().split("\n"):
            if self.Main.cBox_performer_fanside.findText(fan_side, flags=Qt.MatchFlag.MatchExactly) == -1 and fan_side:            
                self.Main.cBox_performer_fanside.addItem(fan_side)        
        infos_webside.set_tooltip_text("cBox_performer_", "fanside", f"Datenbank: {fan_side}", "Datenbank")
        ### --------- Quell Links in QTableWidget setzen -------------- ###        
        errview, ids, links, images, aliases = datenbank_darsteller.get_quell_links(self.Main.tblWdg_Daten.selectedItems()[0].text()) #ArtistID -> DB_NamesLink.NamesID
        for zeile,(id, link, image, alias) in enumerate(zip(ids,links,images,aliases)):
            self.Main.tblWdg_performer_links.setRowCount(zeile+1)
            self.Main.tblWdg_performer_links.setItem(zeile,0,QTableWidgetItem(f"{id}"))            
            self.Main.tblWdg_performer_links.setItem(zeile,1,QTableWidgetItem(link))
            self.Main.tblWdg_performer_links.setItem(zeile,2,QTableWidgetItem(image))
            self.Main.tblWdg_performer_links.setItem(zeile,3,QTableWidgetItem(alias))
        self.Main.tblWdg_performer_links.resizeColumnsToContents() 
        ### --------- IAFD Link setzen -------------------------------- ###
        self.Main.lnEdit_DBIAFD_artistLink.textChanged.disconnect() # deaktiven
        if self.Main.tblWdg_Daten.selectedItems()[2].text():                                 
            infos_webside.set_daten_in_maske("lnEdit_DB", "IAFD_artistLink", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[2].text(), artist=True) 
            self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)
            self.Main.lbl_checkWeb_IAFD_artistURL.setText("Check OK !")
        elif self.Main.chkBox_get_autom_iafd.isChecked():
             self.Main.lnEdit_IAFD_performer.setText(self.Main.tblWdg_Daten.selectedItems()[1].text())            
             iafd_infos.get_IAFD_performer_link() 
             self.Main.Btn_Linksuche_in_IAFD_artist.setEnabled(True)   
        self.Main.lnEdit_DBIAFD_artistLink.textChanged.connect(self.Main.Web_IAFD_artist_change) # aktiven          
        ### --------- BabePedia Link setzen -------------------------------- ###
        if self.Main.tblWdg_Daten.selectedItems()[3].text():
            self.Main.lnEdit_DBBabePedia_artistLink.textChanged.disconnect() # deaktiven         
            infos_webside.set_daten_in_maske("lnEdit_DB", "BabePedia_artistLink", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[3].text(), artist=True) 
            self.Main.lnEdit_DBBabePedia_artistLink.textChanged.connect(self.Main.Web_BabePedia_artist_change) # aktiven 
            self.Main.Btn_performer_in_BabePedia.setEnabled(True)
            self.Main.lbl_checkWeb_BabePedia_artistURL.setText("Check OK !")
        ### ----------- Rest in Maske packen ------------ ###
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "haar", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[16].text(), artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "augen", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[17].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "geburtsort", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[8].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "geburtstag", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[7].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "bodytyp", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[13].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "boobs", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[10].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "aktiv", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[18].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "groesse", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[12].text(),artist=True)
        infos_webside.set_daten_with_tooltip("lnEdit_performer_", "gewicht", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[11].text(),artist=True)
        infos_webside.set_daten_with_tooltip("txtEdit_performer_", "piercing", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[14].text(),artist=True)
        infos_webside.set_daten_with_tooltip("txtEdit_performer_", "tattoo", "Datenbank", self.Main.tblWdg_Daten.selectedItems()[15].text(),artist=True)
        ### ----------- IAFD Image in Label setzen ------- ###
        errview, image_pfad = datenbank_darsteller.get_iafd_image(self.Main.tblWdg_Daten.selectedItems()[0].text())
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            infos_webside.set_tooltip_text("lbl_", "iafd_image", f"Datenbank: '{image_pfad}'", "Datenbank")
            pixmap = QPixmap()
            pixmap.load(str(image_pfad))
        else:
            infos_webside.set_tooltip_text("lbl_", "iafd_image", f"Datenbank: 'Kein Bild gespeichert'", "Datenbank")                              
            pixmap = QPixmap(str(PROJECT_PATH / "grafics/_buttons/kein-bild.jpg"))
            aspect_ratio = pixmap.width() / pixmap.height()        
        self.Main.lbl_iafd_image.setPixmap(pixmap.scaled(238, 280, Qt.AspectRatioMode.KeepAspectRatio))


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
        if errview:
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
            "IAFDLink": self.Main.lnEdit_DBIAFD_artistLink.text(),
            "BabePedia": self.Main.lnEdit_DBBabePedia_artistLink.text(),
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
            for zeile in range(self.Main.tblWdg_performer_links.rowCount()):
                row_data = {
                    "NamesID": int(self.Main.tblWdg_performer_links.item(zeile, 0).text()),
                    "Link": self.Main.tblWdg_performer_links.item(zeile, 1).text(),
                    "Image": self.Main.tblWdg_performer_links.item(zeile, 2).text(),
                    "Alias": self.Main.tblWdg_performer_links.item(zeile, 3).text()
                }
                names_link_satz.append(row_data)
        return daten_satz, names_link_satz, nation_message
    
    def update_names_linksatz_in_ui(self, artist_id: int):
        datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
        errview, ids, links, images, aliases = datenbank_darsteller.get_quell_links(artist_id) #ArtistID -> DB_NamesLink.NamesID
        for zeile, (id, link, image, alias) in enumerate(zip(ids,links,images,aliases)):                   
            self.Main.tblWdg_performer_links.setRowCount(zeile+1)
            self.Main.tblWdg_performer_links.setItem(zeile,0,QTableWidgetItem(f"{id}"))            
            self.Main.tblWdg_performer_links.setItem(zeile,1,QTableWidgetItem(link))
            self.Main.tblWdg_performer_links.setItem(zeile,2,QTableWidgetItem(image))
            self.Main.tblWdg_performer_links.setItem(zeile,3,QTableWidgetItem(alias))
        self.Main.tblWdg_performer_links.update()
        self.Main.tblWdg_performer_links.resizeColumnsToContents()

    
    def put_daten_satz_in_tablewidget(self): 
        daten_satz,_,_ = self.get_artistdata_from_ui()
        artist_id=daten_satz["ArtistID"]
        for zeile in range(self.Main.tblWdg_Daten.rowCount()):
            item = self.Main.tblWdg_Daten.item(zeile, 0)
            if item is not None and str(artist_id) in item.text():
                # Der Text wurde gefunden, tu hier, was du möchtest
                for spalte, (key, value) in enumerate(daten_satz.items()):
                    self.Main.tblWdg_Daten.setItem(zeile, spalte, QTableWidgetItem(str(value)))
                    self.Main.tblWdg_Daten.update()
                    self.Main.tblWdg_Daten.selectRow(zeile)
                return artist_id, zeile+1  
        return 0, 0        

    def update_datensatz(self):
        nameslink_msg: str=""
        is_neu: int=0 
        is_updated: int=0  
        #### --------------- IAFD Image adden ----------------------------- ####
        iafd_message=self.save_iafd_image_in_datenbank()
        #### -------------------------------------------------------------- ####     
        artist_id, zeile= self.put_daten_satz_in_tablewidget()
        daten_satz, names_link_satz, nation_message=self.get_artistdata_from_ui(database=True) 
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
        errview, is_update= datenbank_darsteller.update_performer_datensatz(daten_satz)        
        artist_id = daten_satz["ArtistID"]
        for linksatz  in names_link_satz:
            url=linksatz["Link"]
            studio_link = f"{urlparse(url).scheme}://{urlparse(url).netloc}/"                       
            studio_id = datenbank_darsteller.get_studio_id_from_baselink(studio_link)
            if studio_id > 0:
                datensatz=datenbank_darsteller.get_db_artistlink(linksatz["NamesID"])
                linksatz_list = list(linksatz.values()) # dict values in eine Liste umwandeln zum vergleich mit DB
                if datensatz and datensatz[0]!=linksatz_list[0]: # check ob NamesID gleich ist
                    is_neu += datenbank_darsteller.add_db_artistlink(artist_id, names_link_satz, studio_id)
                else:                                  
                    if linksatz_list != datensatz: # wenn gleich, dann check ob sich was verändert hat
                        is_updated += datenbank_darsteller.update_performer_names_link(artist_id, linksatz, studio_id)                    
        if (is_neu or is_updated) > 0:
            self.update_names_linksatz_in_ui(daten_satz["ArtistID"])
            nameslink_msg="NamesLink"
        datensatz_errview=None
        if not errview and is_update:
            datensatz_message=f"Datensatz und"
        else:
            datensatz_message=""
            datensatz_errview=errview
                
        #### --------------------------------------------------------------- ####        
        if not errview and is_update:
            message=f"Datensatz: {artist_id} in Zeile: {zeile} wurde {datensatz_message} {nameslink_msg} updatet{iafd_message} !"
            QTimer.singleShot(100, lambda :self.Main.lbl_db_status.setStyleSheet('background-color: #74DF00'))            
            QTimer.singleShot(3500, lambda :self.Main.lbl_db_status.setStyleSheet('background-color:'))
        else:
            message=f"Datensatz: {artist_id} in Zeile: {zeile} wurde nicht updatet. Fehler: {errview}, {datensatz_errview}"
            QTimer.singleShot(100, lambda :self.Main.lbl_db_status.setStyleSheet('background-color: #FF0000'))            
            QTimer.singleShot(3500, lambda :self.Main.lbl_db_status.setStyleSheet('background-color:'))
        self.Main.lbl_db_status.setText(message+nation_message)
        
    def save_iafd_image_in_datenbank(self):
        datenbank_darsteller=DB_Darsteller(MainWindow=self.Main)
        artist_id=int(self.Main.grpBox_performer.title().replace("Performer-Info ID: ",""))
        errview,image_pfad = datenbank_darsteller.get_iafd_image(artist_id)
        iafd_message: str=""        
        if not (image_pfad and str(Path(PROJECT_PATH / image_pfad).exists()) or self.Main.lbl_iafd_image.toolTip() == "Kein Bild gespeichert"):
            pixmap = self.Main.lbl_iafd_image.pixmap()
            if pixmap:
                iafd_link=self.Main.lnEdit_DBIAFD_artistLink.text()                
                perfid,_ = iafd_link.replace("https://www.iafd.com/person.rme/perfid=","").split("/",1)
                name = self.Main.lnEdit_performer_info.text()
                image_pfad=f"__artists_Images/{name}/[IAFD]-{perfid}.jpg"
                names_link_iafd = {                        
                        "Link": iafd_link,
                        "Image": image_pfad,
                        "ArtistID": artist_id,
                        "Alias": name
                    }
                errview, is_addet = datenbank_darsteller.add_performer_iafd_image(names_link_iafd) 
                if is_addet:
                    iafd_message=", IAFD Bild wurde gespeichert" 
                    if not Path(Path(PROJECT_PATH / image_pfad).parent).exists():
                        Path(PROJECT_PATH / image_pfad).parent.mkdir()        
                    pixmap.save(str(PROJECT_PATH / image_pfad), "JPEG")
                    self.update_names_linksatz_in_ui(artist_id)
        return iafd_message


    def clear_maske(self):
        felder = ["sex", "rasse", "nation", "haar", "augen", "geburtsort", "geburtstag", "boobs", "bodytyp", "aktiv", "groesse",
                "gewicht", "piercing", "tattoo"]
        self.Main.tooltip_claering(felder)
        self.Main.lbl_iafd_image.clear()
        self.Main.lbl_link_image_from_db.clear()
        self.Main.lbl_db_status.setText("")
        self.Main.lbl_performer_link.setText("")
        self.Main.grpBox_performer.setTitle("Performer-Info für:")
        self.Main.lnEdit_performer_info.setText("")
        self.Main.lnEdit_DBIAFD_artistLink.setText("")
        self.Main.lnEdit_DBBabePedia_artistLink.setText("")
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







# Abschluss
if __name__ == '__main__':
    PerformerInfosMaske()