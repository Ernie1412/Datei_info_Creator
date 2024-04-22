from PyQt6.QtWidgets import QTableWidgetItem


from gui.helpers.message_show import MsgBox
from utils.database_settings import ScrapingData, VideoData

class SearchTitle:
    def __init__(self, MainWindow):
        super().__init__()
        self.Main = MainWindow
    
    def search_title(self):
        self.Main.tblWdg_daten.setRowCount(0)        
        if self.Main.sender() == self.Main.Btn_Titelsuche_in_DB:
            studio = self.Main.Btn_logo_am_db_tab.toolTip()             
            titel_db = self.replace_special_chars(self.Main.lnEdit_db_titel.text())

            self.Main.lnEdit_db_titel.setText(titel_db)
        else: 
            studio = self.Main.lbl_SuchStudio.text()   
            titel_db = self.replace_special_chars(self.Main.lnEdit_analyse_titel.text())

            self.Main.lnEdit_db_titel.setText(titel_db) 
        if self.Main.is_studio_in_database(studio):
            self.Main.lnEdit_db_titel.setText(self.Main.lnEdit_analyse_titel.text())
            self.get_video_data_from_database(studio, titel_db)
        else:
            MsgBox(self, f"Es gibt noch keine Datenbank für: <{studio}>","w")

    def linksuche_in_db(self):        
        link = self.Main.lnEdit_URL.text()
        studio = self.Main.lnEdit_Studio.text() 

        if self.Main.is_studio_in_database(studio):
            scraping_data = ScrapingData(MainWindow=self.Main)
            errorview = scraping_data.hole_link_aus_db(link, studio)
            if errorview:
                MsgBox(self.Main, errorview, "w") 
            else:                                
                self.tabelle_erstellen_fuer_movie(studio, link)              
                #self.set_datas_in_database()
        else:
            MsgBox(self.Main, f"Es gibt noch keine Datenbank für: <{studio}>","w")
    
    def performer_suche_in_scene(self):
        self.Main.tblWdg_performer.clear()
        if self.Main.sender() == self.Main.Btn_perfomsuche_in_DB: # Button auf den Movie Datenbank Tab/Stacked
            studio = self.Main.Btn_logo_am_db_tab.toolTip()
            name_db = self.Main.lnEdit_db_performer.text()
        elif self.Main.rBtn_set_actorname_site.isChecked():
            studio = self.Main.lbl_SuchStudio.text()
            name_db = self.Main.lnEdit_analyse_actor_site.text()
        else:                                           # Button auf den Analyse Tab/Stacked
            studio = self.Main.lbl_SuchStudio.text()
            name_db = self.Main.cBox_performers.currentText()                
        
        if self.Main.is_studio_in_database(studio):
            scraping_data = ScrapingData(MainWindow=self.Main)
            errorview = scraping_data.hole_videodatas_von_performer(name_db, studio)  # erstellt auch in tblWdg_daten die Liste          
            if errorview:
                MsgBox(self.Main, errorview,"w") 
            else:  
                self.tabelle_erstellen_fuer_movie(studio, name_db)
        else:
            MsgBox(self.Main, f"Es gibt noch keine Datenbank für: <{studio}>","w")

    #### --------------- Video Info Tabelle ----------------------- ###
    def get_video_data_from_database(self, studio, title_db):
        scraping_data = ScrapingData(MainWindow=self.Main)
        errorview = scraping_data.hole_titel_aus_db(title_db, studio)
        if errorview:
            MsgBox(self, errorview,"w") 
        else: 
            self.tabelle_erstellen_fuer_movie(studio, title_db)

    ### ------------------------ Movie Info Tabelle ----------------------- ###
    def get_header_for_movie_table(self):
        return ["ID", "Titel", "WebSideLink", "IAFDLink", "Performers", "Alias", "Action","Dauer", "ReleaseDate", "ProductionDate",
                "Serie","Regie","SceneCode","Movies","Synopsis","Tags"]

    def tabelle_erstellen_fuer_movie(self, studio, title):
        zeile: int = 0
        self.Main.tblWdg_daten.setProperty("studio",studio)
        self.Main.stacked_tables.setCurrentWidget(self.Main.stacked_page_table_daten)        
        video_data_json=VideoData().load_from_json()
        if not video_data_json:
            MsgBox(self.Main, f"Kein Eintrag für {title} in Studio: {studio}","w")
            return
        header_labels = self.get_header_for_movie_table()  
        self.Main.tblWdg_daten.setColumnCount(len(header_labels))
        self.Main.tblWdg_daten.setHorizontalHeaderLabels(header_labels)      
        for zeile, video_data in enumerate(video_data_json):            
            self.Main.tblWdg_daten.setRowCount(zeile+1)
            for column, db_feld_name in enumerate(header_labels): 
                self.Main.tblWdg_daten.setItem(zeile, column, QTableWidgetItem(f'{video_data[db_feld_name]}'))
        self.Main.tblWdg_daten.setCurrentCell(zeile, 0)

    def replace_special_chars(self, string):
        if not string:
            return ""
        escape_dict = {
                "'": "''",
                '"': '""',
                "\\": "\\\\",
                "\%": "\\%",
                "_": "\\_",
                "\[": "\\[",
                "\]": "\\]",     }       
        for char, escaped_char in escape_dict.items():
            string = string.replace(char, escaped_char)
        return string