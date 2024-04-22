from PyQt6.QtWidgets import QScrollArea, QHBoxLayout, QWidget, QLabel, QTableWidgetItem
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from tldextract import extract

class SetActorInfos():

    def __init__(self, scrape_actor_infos):
        self.scrape_actor_infos = scrape_actor_infos                

    def set_aliases_in_lineedit(self, aliases: list) -> None:
        if not aliases:
            return
        self.scrape_actor_infos.lnEdit_performer_aliases.setText(', '.join(aliases[0]))

    def set_gender_button(self, gender: str) -> None:
        if not gender:
            self.scrape_actor_infos.Btn_actor_gender_sign.setIcon(QIcon(":Buttons\_buttons\gender\fragezeichen.png"))
            self.scrape_actor_infos.Btn_actor_gender_sign.setProperty("gender", "Unbekannt")
            return
        if gender == "Male":
            self.scrape_actor_infos.Btn_actor_gender_sign.setIcon(QIcon(":Buttons\_buttons\gender\person-maennlich.png"))
            self.scrape_actor_infos.Btn_actor_gender_sign.setProperty("gender", "Male")
        elif gender == "Female":
            self.scrape_actor_infos.Btn_actor_gender_sign.setIcon(QIcon(":Buttons\_buttons\gender\person-weiblich.png"))
            self.scrape_actor_infos.Btn_actor_gender_sign.setProperty("gender", "Female")
        else:        
            self.scrape_actor_infos.Btn_actor_gender_sign.setIcon(QIcon(":Buttons\_buttons\gender\person-trans.png"))
            self.scrape_actor_infos.Btn_actor_gender_sign.setProperty("gender", "Trans Female") 
    

    def set_actor_site_performers(self, site_performers: list) -> None:
        if not site_performers:
            return 
        site_extra = []
        self.scrape_actor_infos.tblWgd_arctor_links.setRowCount(len(site_performers))
        header_labels = self.get_site_extras()  
        self.scrape_actor_infos.tblWgd_arctor_links.setColumnCount(len(header_labels))
        self.scrape_actor_infos.tblWgd_arctor_links.setHorizontalHeaderLabels(header_labels)
        for zeile, name in enumerate(site_performers): 
            site_name = name['site'].get('name')                        
            self.scrape_actor_infos.tblWgd_arctor_links.setItem(zeile, 0, QTableWidgetItem(f"{site_name}"))
            self.scrape_actor_infos.tblWgd_arctor_links.setItem(zeile, 1, QTableWidgetItem(f"{name.get('name')}"))
            self.scrape_actor_infos.tblWgd_arctor_links.setItem(zeile, 2, QTableWidgetItem(f"{name.get('slug')}"))
            for idx, extra in enumerate(header_labels[2:]):
                if name.get('parent'):
                    site_extra = name['parent']['extras'].get(extra)
                    self.scrape_actor_infos.tblWgd_arctor_links.setItem(zeile, idx+2, QTableWidgetItem(f'{site_extra}'))
        self.scrape_actor_infos.tblWgd_arctor_links.setCurrentCell(0, 0)

    def set_medialink_in_table(self, medialinks: list) -> None:
        self.medialinks_from_theporndb = {}
        if not medialinks:
            return                   
        header_labels = ["Website", "URL"]        
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.setRowCount(len(medialinks))
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.setColumnCount(len(header_labels))
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.setHorizontalHeaderLabels(header_labels)
        self.scrape_actor_infos.lblactor_medialinks_from_api.setText(f"Vom Server: ({len(medialinks)} Links)")
        for zeile, (media_name, media_link) in enumerate(medialinks.items()):
            if media_link:
                self.medialinks_from_theporndb[media_name] = media_link           
            self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.setItem(zeile, 0, QTableWidgetItem(f'{media_name}'))
            self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.setItem(zeile, 1, QTableWidgetItem(f'{media_link}'))
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_api.resizeColumnsToContents()

    def set_medialink_from_mydb_in_table(self) -> None:
        medialinks = self.scrape_actor_infos.get_medialinks_from_mydb()
        medialinks = self.scrape_actor_infos.get_socialmedia_from_mydb(medialinks)
        medialinks = self.scrape_actor_infos.get_iafd_from_mydb(medialinks)
        header_labels = ["Website", "URL"]   
        zeile = 0 
        diff = len(medialinks) - len(self.medialinks_from_theporndb)
        self.scrape_actor_infos.lblactor_medialinks_from_mydb.setText(f"Datenbank: - {len(medialinks)} = {diff})")
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.setColumnCount(len(header_labels))
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.setHorizontalHeaderLabels(header_labels)
        if len(self.medialinks_from_theporndb):
            medialinks.update(self.medialinks_from_theporndb)
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.setRowCount(len(medialinks)) 
        for media_name, media_link in medialinks.items():                        
            self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.setItem(zeile, 0, QTableWidgetItem(f'{media_name}'))
            self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.setItem(zeile, 1, QTableWidgetItem(f'{media_link}'))
            zeile +=1 
        self.scrape_actor_infos.tblWdg_actor_medialinks_from_mydb.resizeColumnsToContents()

    def set_actor_image_in_label(self, image_datas: dict) -> None:
        if not image_datas:
            return
        elif image_datas == "403":
            self.scrape_actor_infos.lbl_scene_image.setStyleSheet('background-image:url(:/label/labels/403 Forbidden.jpg);')
            return
        self.scrape_actor_infos.lbl_image_counter.setText(f"{len(image_datas)} Bilder")
        scroll_area = self.scrape_actor_infos.findChild(QScrollArea, "scrollArea_actor_images")
        # QVBoxLayout für das QScrollArea-Widget erstellen
        layout = QHBoxLayout()
        for idx in range(len(image_datas)):            
            for image_link, image_data in image_datas[idx].items(): 
                setattr(self.scrape_actor_infos, f"lbl_image{idx}", QLabel()) 
                label = getattr(self.scrape_actor_infos, f"lbl_image{idx}") 
                if image_data:
                    pixmap = QPixmap() 
                    pixmap.loadFromData(image_data)
                    scaled_pixmap = pixmap.scaled(170, 256, Qt.AspectRatioMode.KeepAspectRatio)
                    label.setPixmap(scaled_pixmap)
                else:
                    label.setText(f"Bild {idx}")
                    label.setFixedSize(170, 256)                     
                    label.setStyleSheet("QLabel {font-size: 32pt;font-weight: bold;width: 170px;height: 256px;border: 1px solid black;}")
                label.setToolTip(image_link) 
                layout.addWidget(label)
            widget = QWidget()
            widget.setLayout(layout)
            # Größe des Widget an die Anzahl der Bilder anpassen
            widget.setFixedSize(widget.sizeHint())
            # QScrollArea-Widget das Layout setzen
            scroll_area.setWidget(widget)        
    
    def set_api_value_in_combobox(self, api_value: str, widget) -> None:
        combo = getattr(self.scrape_actor_infos,f"cBox_performer_{widget}")
        if not api_value:
            combo.setCurrentIndex(-1)
            return        
        index = combo.findText(api_value)
        if index >= 0: 
            combo.setCurrentIndex(index)   


    ### --------------------------- get informations -------------------------------- ###    
    def get_socialmedia_name_from_link(self, link: str) -> str:        
        social = {"instagram": "Instagram", 
                "facebook": "Facebook", 
                "twitter": "Twitter", 
                "youtube": "Youtube", 
                "snapchat": "Snapchat", 
                "fansly": "Fansly", 
                "fancentro": "FanCentro", 
                "onlyfans": "OnlyFans", 
                "linktr": "Linktree", 
                "loyalfans": "LoyalFans", 
                "twitch": "Twitch", 
                "manyvids": "Manyvids",
                "tiktok": "TikTok",
                "imdb": "IMDB"}
        extrakt_link = extract(link).domain
        return social.get(extrakt_link, '') 
    
    def get_site_extras(self) -> list:
        return ["Site-Name","Name", "birthplace", "ethnicity", "eye_colour", "haircolor", "fakeboobs", "gender",
                "height", "measurements", "nationality", "piercings", "tattoos", "weight"] 