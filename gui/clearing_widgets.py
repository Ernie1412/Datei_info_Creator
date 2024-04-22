from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap

from pathlib import Path

from gui.context_menus.context_menu_for_buttons import CustomMenuButtons

from config import WEBINFOS_JSON_PATH, PROJECT_PATH


class ClearingWidget():
    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow

        #### ----- einiges Labels erstmal unsichtbar setzen ----- ####
    ##############################################################
    def invisible_database_link(self):
        self.Main.Btn_pornbox_links.setVisible(False)

    def invisible_movie_btn_anzahl(self):
        lbl_anzahl_db: list = ["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Movies", "Synopsis", "Tags"]        
        for anzahl in lbl_anzahl_db:
            getattr(self.Main, f"Btn_Anzahl_DB{anzahl}").setVisible(False)
        
    def invisible_performer_btn_anzahl(self):
        performers_button_selections = ["hair", "eye", "rasse", "birthplace", "birthday", "height", "boobs", "tattoo", "piercing", "body", "weight", "activ"]
        for button_selection in performers_button_selections:
            button = getattr(self.Main, f"Btn_{button_selection}_selection")
            button.setVisible(False)
            button.setText("")

    def reset_bio_website_image_on_stacked(self):
        for biosite in self.Main.get_bio_websites(widget=True):
            label = getattr(self.Main, f"Btn_{biosite}_image")
            label.setProperty("name", "")
            tool_tip = label.toolTip().replace(biosite, "Datenbank")
            label.setToolTip(tool_tip)
    
    def invisible_any_labels(self):
        labels: list = ["SceneCode", "ProDate", "Regie", "_checkWeb_data18URL", "_checkWeb_theporndbURL", "_checkWeb_iafdURL"]
        line_edits: list = ["ProDate","Regie"]
        for label in labels:
            getattr(self.Main, f"lbl{label}").setVisible(False)
        for line_edit in line_edits:
            getattr(self.Main, f"lnEdit_{line_edit}").setVisible(False)

    ### ------------ Seiten wie Bangbros zusätliche Infos sichtbar machen ------------------ ###
    def special_infos_visible(self, bolean: bool) -> None:
        infos=["lblSceneCode","lblProDate", "lblRegie", "lnEdit_SceneCode", "lnEdit_ProDate","lnEdit_Regie"]
        for info in infos:
            getattr(self.Main,info).setEnabled(bolean)
    ##############################################################
            
    ### ---------------- reset ui elements auf dem Datenbank Tab -------------------------- ###       
    def loesche_DB_maske(self):
        line_edit_dbs=["SceneCode", "ProDate", "Release", "Regie", "Serie", "Dauer", "Data18Link", "ThePornDBLink", "IAFDLink"]        
        text_edit_dbs=["Movies", "Tags", "Synopsis"] 

        for line_edit_db in line_edit_dbs:
            getattr(self.Main, f"lnEdit_DB{line_edit_db}").clear()
               
        for text_edit_db in text_edit_dbs:
            getattr(self.Main, f"txtEdit_DB{text_edit_db}").clear()
    ### ------------------------------------------------------------------------------------ ###
    
    def clear_label_and_tooltip(self, widget_name):        
        widget = getattr(self.Main, f"lbl_{widget_name}", None) # falls nicht gefunden dann None Ausgabe
        if widget:
            widget.clear()  
            widget.setToolTip("")

    def clear_line_edit_and_tooltip(self, widget_name):
        widget = getattr(self.Main, f"lnEdit_{widget_name}", None)
        if widget:
            widget.clear()  
            widget.setToolTip("")

    ### ----------------- Tooltips löschen ----------------------------- ####
    def tooltip_claering(self, widget_name: str=None, artist: bool=False) -> None:        
        if artist:
            prefixes =["cBox_performer_", "lnEdit_performer_", "txtEdit_performer_"]
        else:
            prefixes =["lnEdit_DB", "txtEdit_DB"]        
        for prefix in prefixes:
            widget_obj = getattr(self.Main, f'{prefix}{widget_name}', None)
            if widget_obj:
                widget_obj.setToolTip("")
                break
    
    def performers_tab_widgets(self, type_of_widget: str) -> list:
        widget_list=[]
        iafd_artist = ["IAFD_artistAlias", "DBWebSite_artistLink"]
        lineedits = ["hair", "birthplace", "birthday", "boobs", "body", "activ", "height", "weight"]
        tooltips = ["sex", "rasse", "nation", "fanside"]
        textedits = ["piercing", "tattoo"]
        combos = ["eye", "rasse"]
        if "tooltip" in type_of_widget:
            widget_list.append(tooltips + lineedits + textedits)
        if "line_" in type_of_widget:
            widget_list.append(lineedits)
        if type_of_widget == "text":
            widget_list.append(textedits)
        if "performer" in type_of_widget:            
            for lineedit in lineedits:
                widget_list.append(f"performer_{lineedit}") 
        if "lineprefix_perf" in type_of_widget:            
            for lineedit in lineedits:
                widget_list.append(f"lnEdit_performer_{lineedit}")
        if "textprefix_perf" in type_of_widget:            
            for textedit in textedits:
                widget_list.append(f"txtEdit_performer_{textedit}")
        if "lineiafd" in type_of_widget:
            for artist in iafd_artist:
                widget_list.append(f"lnEdit_{artist}") 
        if "iafd_" in type_of_widget:
            for artist in iafd_artist:
                widget_list.append(artist)
        if "combo_perf" in type_of_widget:
            for combo in combos:
                widget_list.append(f"cBox_performer_{combo}")  
        return widget_list

    def clear_maske(self):
        bio_website_list = self.Main.get_bio_websites(widget=True)
        self.set_website_bio_enabled(bio_website_list, False)
        a= self.performers_tab_widgets("performer_text_iafd_") 
        bio_website_list.append("link_image_from_db")                
        elements_to_reset = [
            (self.tooltip_claering, self.performers_tab_widgets("tooltip")),            
            (self.clear_label_and_tooltip, bio_website_list),
            (self.clear_line_edit_and_tooltip, self.performers_tab_widgets("performer_line_iafd_")),
            (self.clear_combobox_and_list, ["performer_rasse", "performer_eye"]),
            (self.clear_text_edit, self.performers_tab_widgets("textprefix_perf")),
            (self.set_default_table, ["performer_links"]),
            (self.clear_nations, [0,1,2,3,4,5,6]),
            (self.clear_social_media, [0,1,2,3,4,5,6,7,8,9])    ]
        for method, widgets in elements_to_reset:
            for widget in widgets:
                if  method==self.tooltip_claering:
                    method(widget, True)           
                else:
                    method(widget)
        self.Main.grpBox_performer_name.setTitle("Performer-Info für:")  
        Path(WEBINFOS_JSON_PATH).unlink(missing_ok=True) 
        Path(PROJECT_PATH / "iafd_performer.jpg").unlink(missing_ok=True) 
        self.Main.Btn_IAFD_perfomer_suche.setEnabled(False)
        self.Main.Btn_IAFD_perfomer_suche.setToolTip("Geschlecht auswählen !")  

    def clear_combobox_and_list(self,widget_name: str ) -> None:        
        widget = getattr(self.Main, f"cBox_{widget_name}", None)
        if widget and widget_name in ["performer_rasse"]: 
            widget.uncheck_all_items() # CustomQComboBox Einstellung
        else:
            widget.setCurrentIndex(0)    
        widget.setToolTip("")    

    def clear_text_edit(self,widget_name: str ) -> None:
        widget = getattr(self.Main, f"{widget_name}", None)
        if widget:
            widget.setPlainText("")

    def set_default_table(self,widget_name: str ) -> None:
        widget = getattr(self.Main, f"tblWdg_{widget_name}", None)
        if widget:
            widget.clearContents()
            widget.setRowCount(0)
    
    def clear_nations(self, widget_name: str ) -> None:
        widget = getattr(self.Main, f"lbl_performer_nation_{widget_name}", None)
        if widget: 
            widget.setProperty("nation","")
            widget.setStyleSheet("")  
            widget.setToolTip("")           

    def clear_social_media_in_buttons(self) -> None:
        for i in range(10):
            self.clear_social_media(f"{i}")

    def clear_social_media(self, widget_name: str ) -> None:
        widget = getattr(self.Main, f"Btn_performers_socialmedia_{widget_name}", None)
        if widget:
            widget.setProperty("socialmedia","")
            widget.setStyleSheet("")
            widget.setToolTip("")
            widget.setVisible(False)

    ### Elemente ausschalten, sichtbar, unsichtbar machen, um unnötige Abfragen zu verhindern ###
    def tabs_clearing(self, tab_dateiinfo: bool=True, tab_fileinfo: bool=True, analyse_button: bool=True, table_files: bool=True) -> None:        
        if not tab_dateiinfo:
            line_edits=["Studio", "URL", "IAFDURL", "Titel", "ThePornDBURL","NebenSide", "ErstellDatum", "ProJahr", "ProDate", "Regie", "SceneCode"]
            list_widgets=["Darstellerin","Darsteller"]
            text_edits=["Tags","Beschreibung","Movies"]

            for line_edit in line_edits:
                getattr(self.Main, f"lnEdit_{line_edit}").clear()

            for list_widget in list_widgets:
                getattr(self.Main, f"lstWdg_{list_widget}").clear()

            for text_edit in text_edits:
                getattr(self.Main, f"txtBrw_{text_edit}").clear()

            self.Main.lbl_datei_info_fuer.clear()

        if not table_files:
            self.Main.tblWdg_files.clearContents()

        if not tab_fileinfo:
            labels=["Bitrate", "FrameRate", "VideoArt", "FileCreation", "FileSize", "Resize", "Dauer"]            
            for label in labels:
                getattr(self.Main, f"lbl_{label}").clear()

        if not analyse_button:    
            self.Main.lbl_SuchStudio.clear()
            icon_logo, studio = self.Main.set_nologo_button()
            self.Main.Btn_logo_am_analyse_tab.setIcon(icon_logo) 
            self.Main.Btn_logo_am_analyse_tab.setToolTip(studio)
                    
        if not (tab_dateiinfo and table_files and analyse_button and table_files): 
            self.Main.cBox_studio_links.clear()
            icon_logo, studio = self.Main.set_nologo_button() 
            self.Main.Btn_logo_am_infos_tab.setIcon(icon_logo) 
            self.Main.Btn_logo_am_infos_tab.setToolTip(studio)
            self.Main.Btn_logo_am_db_tab.setIcon(icon_logo) 
            self.Main.Btn_logo_am_db_tab.setToolTip(studio)
            self.buttons_enabled(False, ["Laden", "Speichern", "Refresh"])

        if self.Main.lbl_Dateiname.text()!="":self.Main.Btn_Speichern.setEnabled(True)


    def enabled_db_buttons(self, bolean: bool) -> None: 
        webside_model = self.Main.lstView_database_weblinks.model()
        data18 = self.Main.lnEdit_DBData18Link
        iafd = self.Main.lnEdit_DBIAFDLink
        theporndb = self.Main.lnEdit_DBThePornDBLink
        button="Btn_Linksuche_in_"
        
        getattr(self.Main,f"{button}ThePornDB").setEnabled(theporndb and bolean)
        getattr(self.Main,f"{button}Data18").setEnabled(bool(data18.text()) and bolean)
        getattr(self.Main,f"{button}IAFD").setEnabled(bool(iafd.text()) and bolean)       

        self.Main.Btn_addDatei.setEnabled(bolean)
        self.Main.Btn_DBUpdate.setEnabled(bolean)            

    def buttons_enabled(self, bolean: bool, buttons: list) -> None:        
        for info in buttons:
            getattr(self.Main,f"Btn_{info}").setEnabled(bolean)

    def set_website_bio_enabled(self, widgets: str, bolean: bool) -> None:  
        icon = QIcon()
        for widget in widgets:
            bio_button = getattr(self.Main, f"Btn_performer_in_{widget}")  
            if bolean:          
                icon.addPixmap(QPixmap(f":/Buttons/_buttons/performer_biosites/{widget}.png"), QIcon.Mode.Normal, QIcon.State.Off)
            else:
                icon.addPixmap(QPixmap(f":/Buttons/_buttons/performer_biosites/{widget}_disabled.png"), QIcon.Mode.Disabled, QIcon.State.Off)
            bio_button.setIcon(icon)
            bio_button.setIconSize(QSize(50, 25)) 
            if not bolean:
                bio_button.setToolTip("")
            
# Abschluss
if __name__ == '__main__':
    ClearingWidget()