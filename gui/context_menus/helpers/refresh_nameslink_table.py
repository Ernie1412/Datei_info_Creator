from PyQt6.QtWidgets import QTableWidgetItem

from pathlib import Path


from utils.database_settings.database_for_darsteller import DB_Darsteller

from config import PROJECT_PATH

class RefreshNameslinkTable():
    def __init__(self, Main, datenbank_performer_maske):
        super().__init__()
        self.Main = Main
        self.datenbank_performer_maske = datenbank_performer_maske

        ### ------------------- Refresh Performer Links Tabelle --------------------------------------- ###
    def refresh_performer_links_tabelle(self): 
        name=self.Main.lnEdit_performer_info.text()
        images: list=[]
        if self.Main.tblWdg_performer_links.rowCount()>-1 and name:            
            datenbank_darsteller = DB_Darsteller(MainWindow=self.Main)
            nameslink_datenbank = datenbank_darsteller.get_quell_links(self.Main.tblWdg_performer.selectedItems()[0].text()) #ArtistID -> DB_NamesLink.NamesID
            for zeile,(id, link, image, alias) in enumerate(zip(*nameslink_datenbank)):
                self.Main.tblWdg_performer_links.setRowCount(zeile+1)
                self.Main.tblWdg_performer_links.setItem(zeile,0,QTableWidgetItem(f"{id}"))            
                self.Main.tblWdg_performer_links.setItem(zeile,1,QTableWidgetItem(link))
                self.Main.tblWdg_performer_links.setItem(zeile,2,QTableWidgetItem(image))
                images.append(PROJECT_PATH / image)
                self.Main.tblWdg_performer_links.setItem(zeile,3,QTableWidgetItem(alias))
                self.datenbank_performer_maske.set_icon_in_tablewidget(zeile, image)            
            self.Main.tblWdg_performer_links.resizeColumnsToContents()
            self.delete_new_images(images)            
        else:
            self.Main.lbl_db_status.setText("Kein Name oder nichts in der Tabelle drin !") 
    
    def delete_new_images(self, images: list) -> None:
        folder = Path(PROJECT_PATH / "__artists_Images" / self.Main.lnEdit_performer_ordner.text())
        if Path(folder).exists() and self.Main.lnEdit_performer_ordner.text() != "":# alle Dateien, die nicht in 'images' enthalten löschen
            [file.unlink() for file in folder.glob('*') if str(file.name) not in [str(image.name) for image in images]]
        if Path(folder).exists() and len(list(folder.iterdir())) == 0:
            try:
                Path(folder).unlink()
            except FileNotFoundError as e:
                print(f"delete_new_images {e} -> {folder} bei: {images}")
        