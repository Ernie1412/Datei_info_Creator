from pathlib import Path
import json

from config import PROJECT_PATH, WEBINFOS_JSON_PATH


class UpdateThePornDBPerformer:
    def __init__(self, Main, parent):
        self.Main = Main
        self.performer_infos_maske = parent    
    
    def save_theporndb_image_in_datenbank(self, message, errview, datenbank_darsteller, artist_id) -> str: # default ID von der datenbank Maske nehmen  
        image_pfad = datenbank_darsteller.get_biowebsite_image("ThePornDB", artist_id)[1]      
        
        theporndb_link = self.Main.lbl_theporndb_image.toolTip()
        if "Kein Bild" in theporndb_link:            
            return message, errview          
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            self.Main.stacked_webdb_images.setCurrentIndex(1)  # ThePornDB stacked            
            return message, errview  
        name = self.Main.lbl_theporndb_image.property('name')      
        if not self.Main.lbl_theporndb_image.pixmap() and name != "":
            errview['theporndb'] = ".ThePornDB Bild nicht im Label,🚫kein speichern möglich"
            message['theporndb'] = None
            return message, errview         
        ordner = self.Main.lnEdit_performer_ordner.text() 
        image_pfad = f"__artists_Images/{ordner}/[ThePornDB]-{name}.jpg"           
        is_added = False  
        if self.performer_infos_maske.is_ein_bild_dummy_im_label("theporndb") == False:
            pixmap = self.Main.lbl_iafd_image.pixmap()
            self.performer_infos_maske.save_image_to_disk(image_pfad, pixmap)               
            errview['theporndb'], is_added = self.names_link_from_theporndb(image_pfad, theporndb_link, artist_id, datenbank_darsteller)  

            if is_added: # ThePornDB Bild muss verschoben werden             
                message['theporndb'] = ", ThePornDB Bild wurde gespeichert"
                self.Main.stacked_webdb_images.setCurrentIndex(1)  # ThePornDB stacked
            else:
                errview['theporndb'] = f", ThePornDB Bild wurde nicht gespeichert (Error: {errview['theporndb']})"
                message['theporndb'] = None
        return message, errview   
    
    def names_link_from_theporndb(self, image_pfad, theporndb_link, artist_id, datenbank_darsteller):
        ordner = self.Main.lnEdit_performer_ordner.text()        
        pixmap = self.Main.lbl_theporndb_image.pixmap()
        self.performer_infos_maske.save_image_to_disk(image_pfad, pixmap)
        alias = self.Main.lbl_theporndb_image.property("name")             
        names_link_theporndb = {"Link": theporndb_link,
                            "Image": image_pfad,
                            "ArtistID": artist_id,
                            "Alias": alias     } 
        return datenbank_darsteller.add_performer_link_and_image(names_link_theporndb)