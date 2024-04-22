from pathlib import Path
import json


from config import PROJECT_PATH, WEBINFOS_JSON_PATH

class UpdateIAFDPerformer():

    def __init__(self, Main, parent):
        self.Main = Main
        self.performer_infos_maske = parent

    def save_iafd_image_in_datenbank(self, message, errview, datenbank_darsteller, artist_id) -> str: # default ID von der datenbank Maske nehmen  
        image_pfad = datenbank_darsteller.get_biowebsite_image("IAFD", artist_id)        

        iafd_link = self.Main.lnEdit_DBWebSite_artistLink.text()
        if iafd_link == "N/A" and not iafd_link:            
            return message, errview           
        if image_pfad and Path(PROJECT_PATH / image_pfad).exists():
            self.Main.stacked_webdb_images.setCurrentIndex(0)  # IAFD stacked          
            return message, errview        
        if not self.Main.lbl_IAFD_image.pixmap():
            errview['iafd'] = ".IAFD Bild nicht im Label,🚫kein speichern möglich"
            message['iafd'] = None
            return message, errview         
        is_added = False
        image_pfad, perfid = self.get_artist_id_from_folder(errview, message, artist_id, iafd_link, datenbank_darsteller) 
        if self.performer_infos_maske.is_ein_bild_dummy_im_label("IAFD") == False:                          
            errview['iafd'], is_added = self.names_link_from_iafd(image_pfad, perfid, iafd_link, artist_id, datenbank_darsteller) 

            if is_added: # IAFD Bild muss verschoben werden             
                message['iafd'] = ", IAFD Bild wurde gespeichert" 
                self.Main.stacked_webdb_images.setCurrentIndex(0)  # IAFD stacked            
            else:
                errview['iafd'] = f", IAFD Bild wurde nicht gespeichert (Error: {errview['iafd']})"
                message['iafd'] = None
        return message, errview
    
    def get_artist_id_from_folder(self, errview, message, artist_id, iafd_link, datenbank_darsteller) -> tuple:
        ordner = self.Main.lnEdit_performer_ordner.text()
        perfid = self.get_perfid_from_iafd_link(iafd_link)
        if not perfid:
            errview['iafd'] = ".Es ist kein IAFD Link  !"
            message['iafd'] = None
            return message, errview
        image_pfad = f"__artists_Images/{ordner}/[IAFD]-{perfid}.jpg"
        if Path(image_pfad).exists():
            _artist_id = datenbank_darsteller.get_artistid_from_nameslink(image_pfad)
            if artist_id != _artist_id:
                print(f"{artist_id}!= {_artist_id}")        
        return image_pfad, perfid 
    
    def names_link_from_iafd(self, new_image_pfad, perfid, iafd_link, artist_id, datenbank_darsteller):
        infos: dict={}
        if not Path(WEBINFOS_JSON_PATH).exists(): # get iafd_infos from ui
            iafd_infos = {"alias": self.Main.lnEdit_IAFD_artistAlias.text(),
                          "image_pfad": new_image_pfad}
        else:
            infos = json.loads(WEBINFOS_JSON_PATH.read_bytes())
            iafd_infos = infos.get("iafd","")
        alias = iafd_infos.get("alias","")
        
        
        old_image_pfad = iafd_infos.get("image_pfad","")

        if old_image_pfad:
            iafd_infos["image_pfad"] = str(Path(PROJECT_PATH, new_image_pfad))
            if not Path(Path(PROJECT_PATH / new_image_pfad).parent).exists():
                Path(Path(PROJECT_PATH / new_image_pfad).parent).mkdir()
            if Path(old_image_pfad).exists() and old_image_pfad != new_image_pfad:
                Path(old_image_pfad).rename(Path(PROJECT_PATH, new_image_pfad))
            else:
                new_image_pfad = None
                iafd_infos["image_pfad"] = None        
            infos["iafd"] = iafd_infos
            json.dump(infos,open(WEBINFOS_JSON_PATH,'w'),indent=4, sort_keys=True)
        names_link_iafd = {"Link": iafd_link,
                            "Image": new_image_pfad,
                            "ArtistID": artist_id,
                            "Alias": alias     }  
        #self.performer_infos_maske.update_names_linksatz_in_ui(artist_id) 
        return datenbank_darsteller.add_performer_link_and_image(names_link_iafd)
    
    def get_perfid_from_iafd_link(self, iafd_link):
        try:
            return iafd_link.replace("https://www.iafd.com/person.rme/perfid=", "").split("/", 1)[0]
        except ValueError:
            return None