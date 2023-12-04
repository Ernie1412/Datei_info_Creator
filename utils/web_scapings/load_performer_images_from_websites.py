from PyQt6.QtGui import QPixmap 
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem

import requests
from lxml import html


from config import HEADERS, PROJECT_PATH


class LoadAnalVidsPerformerImages():

    def __init__(self, name, MainWindow):
        super().__init__() 
        self.Main = MainWindow
        self.name = name                
        
    
    def load_analvids_image_in_label(self):        
        url = self.Main.tblWdg_performer_links.selectedItems()[1].text()
        zeile = self.Main.tblWdg_performer_links.currentRow()
        try:
            response = requests.get(url, headers=HEADERS, timeout=10) # Link in der Tabelle    
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            self.Main.lbl_db_status.setText(f"TimeOutError: {e}")             
            return
        content = html.fromstring(response.content) 
        image_url = content.xpath("//div[@class='model__left model__left--photo']/img")
        name_element = content.xpath("//h1[@class='model__title']")
        alias=""
        if name_element:
            alias=name_element[0].text_content()
        if image_url:
            image_url = image_url[0].get("src")
            response = requests.get(image_url, headers=HEADERS)
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)        
            label_height = 280
            try:
                label_width = int(label_height * pixmap.width() / pixmap.height())
            except ZeroDivisionError as e:
                self.Main.lbl_db_status.setText(f"{self.Main.lnEdit_performer_info.text()} --> Fehler: {e}")
                return
            self.Main.lbl_link_image_from_db.setPixmap(pixmap.scaled(label_width, label_height, Qt.AspectRatioMode.KeepAspectRatio))
            id=url.replace("https://www.analvids.com/model/","").split("/",1)[0]
            image_pfad=f"__artists_Images/{self.name}/[AnalVids]-{id}.jpg"
            pixmap.save(str(PROJECT_PATH / image_pfad), "JPEG")
            self.Main.tblWdg_performer_links.setItem(zeile,2,QTableWidgetItem(image_pfad))
            self.Main.tblWdg_performer_links.setItem(zeile,3,QTableWidgetItem(alias))

if __name__ == '__main__':
    pass


