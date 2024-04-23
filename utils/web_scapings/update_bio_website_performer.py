from PyQt6.QtWidgets import QWidget

from pathlib import Path

from config import PROJECT_PATH

class UpdateBioWebSitePerformer:
    def __init__(self, Main, parent):
        self.Main = Main
        self.performer_infos_maske = parent    
    
    def save_biowebsite_image_in_datenbank(self, message, errview, datenbank_darsteller, artist_id, biosite) -> str: # default ID von der datenbank Maske nehmen  
        image_pfad = datenbank_darsteller.get_biowebsite_image(biosite, artist_id)
        biosite_low = biosite.lower()      
        
        label = getattr(self.Main, f"lbl_{biosite}_image")
        biosite_link = label.toolTip()
        if "Kein Bild" in biosite_link:            
            return message, errview   
        page = self.Main.stacked_webdb_images.findChild(QWidget, f"stacked_{biosite_low}_label")       
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            self.Main.stacked_webdb_images.setCurrentWidget(page)  # ThePornDB stacked            
            return message, errview 
        name = label.property('name')      
        if not label.pixmap() and name != "":
            errview[biosite_low] = f".{biosite} Bild nicht im Label,🚫kein speichern möglich"
            message[biosite_low] = None
            return message, errview         
        ordner = self.Main.lnEdit_performer_ordner.text() 
        image_pfad = f"__artists_Images/{ordner}/[{biosite}]-{name}.jpg"           
        is_added = False  
        if self.performer_infos_maske.is_ein_bild_dummy_im_label(biosite) == False:
            pixmap = label.pixmap()
            self.performer_infos_maske.save_image_to_disk(image_pfad, pixmap)               
            errview[biosite_low], is_added = self.get_link_dict(image_pfad, label, biosite_link, artist_id, datenbank_darsteller)  

            if is_added: # ThePornDB Bild muss verschoben werden             
                message[biosite_low] = f", {biosite} Bild wurde gespeichert"                                
                self.Main.stacked_webdb_images.setCurrentWidget(page)# Als aktuelle Seite setzen 
                label.setToolTip(f"Datenbank: {image_pfad}") 
                label.setProperty("name","")              
            else:
                errview[biosite_low] = f", {biosite} Bild wurde nicht gespeichert (Error: {errview[biosite_low]})"
                message[biosite_low] = None
        return message, errview   
    
    def get_link_dict(self, image_pfad, label, biosite_link, artist_id, datenbank_darsteller):                
        pixmap = label.pixmap()
        self.performer_infos_maske.save_image_to_disk(image_pfad, pixmap)
        alias = label.property("name")             
        names_link_biosite = {"Link": biosite_link,
                            "Image": image_pfad,
                            "ArtistID": artist_id,
                            "Alias": alias     } 
        return datenbank_darsteller.add_performer_link_and_image(names_link_biosite)