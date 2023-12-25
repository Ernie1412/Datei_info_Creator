from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtCore import QDateTime
from contextlib import contextmanager
from typing import Tuple

from config import SETTINGS_DB_PATH

class SettingsData:

    def __init__(self):
        self.data = {}

    def initialize(self, record):    
        for i in range(record.count()):
            field = record.field(i)
            self.data[field.name()] = field.value()
        

    def get_data(self):        
        return self.data

class Webside_Settings:
   
    def __init__(self, MainWindow):
        super().__init__() 
        self.Main = MainWindow 
    
    @contextmanager
    def managed_query(self):
        query = QSqlQuery(self.db)
        try:
            yield query
        finally:
            query.finish()
            query.clear()

    def open_database(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE",'movie_data_settings')
        self.db.setHostName("localhost")        
        self.db.setDatabaseName(SETTINGS_DB_PATH)
        self.db.open()       
    
    def close_database(self):
        self.db.close()            
        connection_name = self.db.connectionName()
        del self.db
        QSqlDatabase.database(connection_name).close() 
        QSqlDatabase.removeDatabase(connection_name) # Vorhandene Verbindung schließen

    ##### ------------ Fehler-Behandlung ---------------- ##########
    ################################################################
    def db_fehler(self,fehler: str) -> None:
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        if fehler.startswith("kein"):
            self.Main.lbl_db_status.setStyleSheet("background-color : #FFCB8F")
        else:
            self.Main.lbl_db_status.setStyleSheet("background-color : #FA5882")
        self.Main.lbl_db_status.setText(f"{current_time} --> {fehler}")   


    ##### ------------ speichere/adde Datenpaket(e) ---------------- ##########
    ###########################################################################
    def add_lastVisite(self, lastVisite: str, studio: str, Page_onSide: str=None) -> None:
        errview: str=None

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("UPDATE WebScrapping_Settings SET lastVisite = :lastVisite, Page_onSide = COALESCE(:Page_onSide,Page_onSide) WHERE Name = :Name;")
                query.bindValue(":lastVisite",lastVisite)
                query.bindValue(":Name",studio)
                query.bindValue(":Page_onSide",Page_onSide)                
                query.exec() 
                errview = f"{query.lastError().text()} (query)" if query.lastError().text() else errview               
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.add_neue_videodaten_in_db.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()


    # def addArtistInfos(self,studio_low,Studio,logo,DateiOrdner,Film,Film_Attri,WebSide,Regie,Artist,Artist_Attri,Artist_Single,Artist_Sleep,Artist_Gross,Artist_Sex,ErstellDatum,ErstellDatum_Art,NebenSide,NebenSide_Attri,Beschreibung,Beschreibung_Attri,Beschreibung_Clicks,Tags,Tags_Attri,Tags_Clicks,Tags_Sleep,Tags_Gross,Titel,Titel_Attri):
    #     errview: str=None

    #     self.open_database()
    #    if self.db.isOpen(): 
    #         with self.managed_query() as query:
    #             query.prepare("SELECT SettingID FROM WebScrapping_Settings WHERE Name = :Name;")
    #             query.bindValue(":Name",Studio)
    #             query.exec()        
    #             if query.next():
    #                 errview = f"{query.lastError().text()} (query)" if query.lastError().text() else errview
    #                 setting_id=query.value("SettingID")  
    #             with self.managed_query() as query:      
    #                 query.prepare("INSERT INTO Scrap_MovieInfos (ArtistID, pornside_low,  SettingID,  logo, DateiOrdner, WebSide,Film,Film_Attri,\
    #                     Regie, Artist, Artist_Attri, Artist_Single, Artist_Sleep, Artist_Gross, Artist_Sex, ReleaseDate, ReleaseDate_Art, NebenSide, \
    #                     NebenSide_Attri, Beschreibung, Beschreibung_Attri, Beschreibung_Clicks, Tags, Tags_Attri, Tags_Clicks, Tags_Sleep, Tags_Gross,\
    #                     Titel, Titel_Attri) VALUES (NULL, :pornside_low, :SettingID, :logo, :DateiOrdner, :WebSide, :Film,:Film_Attri, :Regie, :Artist, \
    #                     :Artist_Attri, :Artist_Single, :Artist_Sleep, :Artist_Gross, :Artist_Sex, :ReleaseDate, :ReleaseDate_Art, :NebenSide, \
    #                     :NebenSide_Attri, :Beschreibung, :Beschreibung_Attri, :Beschreibung_Clicks, :Tags, :Tags_Attri, :Tags_Clicks, :Tags_Sleep, \
    #                     :Tags_Gross, :Titel, :Titel_Attri)")
    #                 query.bindValue(":pornside_low", studio_low)
    #                 query.bindValue(":logo", logo)
    #                 query.bindValue(":DateiOrdner", DateiOrdner)
    #                 query.bindValue(":Film", Film)
    #                 query.bindValue(":Film_Attri", Film_Attri)
    #                 query.bindValue(":WebSide", WebSide)
    #                 query.bindValue(":Regie", Regie)
    #                 query.bindValue(":Artist", Artist)
    #                 query.bindValue(":Artist_Attri", Artist_Attri)
    #                 query.bindValue(":ReleaseDate", ErstellDatum)
    #                 query.bindValue(":NebenSide", NebenSide)
    #                 query.bindValue(":NebenSide_Attri", NebenSide_Attri)
    #                 query.bindValue(":Beschreibung", Beschreibung)
    #                 query.bindValue(":Beschreibung_Attri", Beschreibung_Attri)
    #                 query.bindValue(":Beschreibung_Clicks", Beschreibung_Clicks)
    #                 query.bindValue(":Tags", Tags)
    #                 query.bindValue(":Tags_Attri", Tags_Attri)
    #                 query.bindValue(":Tags_Clicks", Tags_Clicks)
    #                 query.bindValue(":Titel", Titel)
    #                 query.bindValue(":Titel_Attri", Titel_Attri)
    #                 query.bindValue(":SettingID", int(setting_id))
    #                 query.bindValue(":Artist_Single", int(Artist_Single))
    #                 query.bindValue(":Artist_Sleep", int(Artist_Sleep))
    #                 query.bindValue(":Artist_Gross", int(Artist_Gross))
    #                 query.bindValue(":Artist_Sex", int(Artist_Sex))
    #                 query.bindValue(":ReleaseDate_Art", int(ErstellDatum_Art))
    #                 query.bindValue(":Tags_Sleep", int(Tags_Sleep))
    #                 query.bindValue(":Tags_Gross", int(Tags_Gross))         
    #                 query.exec()        
    #     else:
    #         self.db_fehler()
    #     self.db.close()
    ##################################################################
    ##### ------------ updates von Datenpakete ---------------- ######
    ##################################################################
    def update_letzte_seite(self, baselink: str, last_page_number: str) -> str: 
        errview: str = None

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("UPDATE WebScrapping_Settings SET video_last_side = :video_last_side WHERE Homepage = :Link;")
                query.bindValue(":Link",baselink)
                query.bindValue(":video_last_side",last_page_number)                
                query.exec()                               
                errview = f"{query.lastError().text()} (query)" if query.lastError().text() else errview               
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.update_letzte_seite.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview  
    
    ##### ------------ hole ganze Datenpakete ---------------- ######
    #################################################################
    # def hole_suchinfos(self,studio):   ### muss überarbeitet werden !!!
    #     errview: str = None
    #     settings_data = SettingsData()

    #     self.open_database()
    #    if self.db.isOpen():        
    #         with self.managed_query() as query:
    #             query.prepare(f"SELECT ViewAll,WebScrapping_Settings.last_side,WebScrapping_Settings.ein_weiter,WebScrapping_Settings.Artist_page,\
    #                           Maske,Artist,Artist_Attri,Artist_Gross,Titel,Titel_Attri,Link,Link_Attri,Link_Single,Image,Such_Infos.Image_Attri,\
    #                           Such_Infos.Image_Wordcut,Such_Infos.Image_Single,Dauer,Dauer_Attri,Dauer_Single,ReleaseDate,ReleaseDate_Attri,NebenSide,\
    #                           NebenSide_Attri FROM Such_Infos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = \
    #                           Such_Infos.SettingID WHERE Name='{studio}';")
    #             query.exec()        
    #             if query.next():
    #                 video_data = settings_data.initialize(query.record())
                  
    #     return video_data     
    
    def get_videodatas_from_baselink(self, link: str) -> str:              
        errview: str = None
        settings_data = SettingsData()        

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager        
            with self.managed_query() as query:
                query.prepare("SELECT * FROM Such_Infos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = Such_Infos.SettingID WHERE Homepage=:Homepage")
                query.bindValue(":Homepage",link)
                query.exec()        
                while query.next():                    
                    settings_data.initialize(query.record())                    
                    errview = f"{query.lastError().text()} (query1)" if query.lastError().text() else errview
                errview = (errview or f"kein {link} gefunden (query)") if not query.lastError().text() and not settings_data else query.lastError().text()
                errview = f"'{self.get_videodatas_from_baselink.__name__}': {errview} (query)" if errview and "kein " not in str(errview) else errview
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_videodatas_from_baselink.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return errview, settings_data
    
    
    # def query_hole_settings_artist(self, studio): ### muss überarbeit werden ! ###
    #     query = self.managed_query()
    #     query.prepare("SELECT * FROM WebScrapping_Settings WHERE Name=:Name;")
    #     query.bindValue(":Name", studio)
    #     query.exec()
    #     return query ### muss überarbeit werden ! ###
    
    # def hole_settings_artist(self, studio: str) -> Tuple [str, dict]:
    #     errorview: str = None         
    #     settings_data = SettingsData()

    #     self.open_database()        
    #     if self.db.isOpen():
    #         with self.managed_query() as query:
    #             query.prepare("SELECT * From WebScrapping_Settings WHERE Name = :Studio;")
    #             query.bindValue(":Studio", studio) 
    #             if query.next():
    #                 video_data = settings_data.initialize(query.record())
    #                 errorview = query.lastError().text()
    #             else:
    #                 errorview = "keine Daten für Artist"
    #     else:
    #         self.db_fehler("Fehler beim Performer Settings holen (db)",self.db) 
    #     self.db.close()
    #     return errorview, video_data

    ##### ------------ hole einzelne Daten ---------------- ######
    ##############################################################
    # def get_movie_settings_for_titel(self, baselink: str) -> Tuple [str, str, str]:  ### funktion noch nicht in Benutzung ###
    #     errview: str = None
    #     titel: str = None 
    #     titel_attri: str = None

    #     self.open_database()
    #     if self.db.isOpen():        
    #         with self.managed_query() as query:
    #             query.prepare("SELECT Titel, Titel_Attri From Scrap_MovieInfos WHERE WebSide=:link;")
    #             query.bindValue(":link", baselink)
    #             query.exec()        
    #             if query.next(): 
    #                 titel=query.value("Titel")
    #                 titel_attri=query.value("Titel_Attri") 
    #                 errview = query.lastError().text()              
    #             else:
    #                 errview = "kein Titel Daten gefunden"
    #     else:
    #         self.db_fehler("Fehler beim holen von Titel-Settings (db)",self.db)
    #     self.db.close()
    #     return errview, titel, titel_attri    

    def get_movie_settings_for_tags(self, baselink: str) -> Tuple [str, str, str]:
        errview: str= None
        tags: str = None
        tags_attri: str = None
        tags_click: str = None

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager
            with self.managed_query() as query:            
                query.prepare("SELECT Tags, Tags_Attri, Tags_Clicks FROM Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink) 
                query.exec()        
                if query.next():                    
                    tags = query.value("Tags")
                    tags_attri = query.value("Tags_Attri")
                    tags_click = query.value("Tags_Clicks") 
                    errview = f"'{self.get_movie_settings_for_tags.__name__}': {errview} (query1)" if query.lastError().text() else errview
                else:            
                    errview = f"'{self.get_movie_settings_for_tags.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"Keine Daten für {baselink} gefunden (query)")               
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_movie_settings_for_tags.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, tags, tags_attri, tags_click    

    def hole_movie_settings_for_artist(self, baselink: str) -> Tuple [str, list]:
        errview: str= None
        artist: str= None
        artist_gross: str= None

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager       
            with self.managed_query() as query:
                query.prepare("SELECT Artist, Artist_Gross From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink) 
                query.exec()        
                if query.next():                     
                    artist=query.value("Artist")                    
                    artist_gross=query.value("Artist_Gross")  
                    errview = f"'{self.hole_movie_settings_for_artist.__name__}': {errview} (query1)" if query.lastError().text() else errview         
                else:
                    errview = f"'{self.hole_movie_settings_for_artist.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"keine Setting Daten mit dem Link {baselink} für Performers gefunden (query)")               
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_movie_settings_for_artist.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, artist, artist_gross

    def hole_movie_settings_for_nebenside(self, baselink: str) -> Tuple [str, str, str]:
        errview: str= None
        nebenside: str= None        

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager   
            with self.managed_query() as query:
                query.prepare("SELECT NebenSide FROM Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink)
                query.exec()
                if query.next():                     
                    nebenside=query.value("NebenSide") 
                    errview = f"'{self.hole_movie_settings_for_nebenside.__name__}': {errview} (query1)" if query.lastError().text() else errview
                else:  
                    errview = f"'{self.hole_movie_settings_for_nebenside.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"keine Setting Daten mit dem Link {baselink} für Serie, Nebensides gefunden (query)")        
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_movie_settings_for_nebenside.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, nebenside
    
    def hole_artist_image(self, baselink: str) -> Tuple[str, str, str, str]:            
        errview: str= None
        image_url_xpath: str= None
        image_url_attri: str= None
        image_url_title: str= None
        name_element_xpath: str= None
        name_element_attri: str= None
        studio: str= None 
        java: str= None 
        self.open_database()
        if self.db.isOpen():  
            with self.managed_query() as query:
                query_command = "SELECT " \
                "Scrap_ArtistInfos.Name," \
                "Scrap_ArtistInfos.Name_Attri," \
                "Scrap_ArtistInfos.Name_title," \
                "Scrap_ArtistInfos.Image," \
                "Scrap_ArtistInfos.Image_Attri,"\
                "WebScrapping_Settings.Name," \
                "WebScrapping_Settings.java" \
                " FROM WebScrapping_Settings" \
                " INNER JOIN Scrap_ArtistInfos ON " \
                "WebScrapping_Settings.SettingID = Scrap_ArtistInfos.SettingID" \
                " WHERE WebScrapping_Settings.Homepage=:Link;"                
                query.prepare(query_command)
                query.bindValue(":Link", f"{baselink}")
                query.exec()
                if query.next():     
                    image_url_xpath=query.value("Scrap_ArtistInfos.Name") 
                    image_url_attri=query.value("Scrap_ArtistInfos.Name_Attri")
                    image_url_title=query.value("Scrap_ArtistInfos.Name_title")  
                    name_element_xpath=query.value("Scrap_ArtistInfos.Image") 
                    name_element_attri=query.value("Scrap_ArtistInfos.Image_Attri")
                    studio=query.value("WebScrapping_Settings.Name")
                    java=query.value("WebScrapping_Settings.java")
                    errview = f"'{self.hole_artist_image.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:  
                    errview = f"'{self.hole_artist_image.__name__}': {query.lastError().text()} (query)" if query.lastError().text() else f"keine Setting Daten mit dem Link {baselink} für 'Image' gefunden (query)"        
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_artist_image.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return image_url_xpath, image_url_attri, image_url_title, name_element_xpath, name_element_attri, studio, java
    

    def hole_movie_settings_for_dauer(self, baselink: str) -> Tuple [str, str]:
        errview: str= None
        dauer: str= None        

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager          
            with self.managed_query() as query:
                query.prepare("SELECT Dauer From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink) 
                query.exec()        
                if query.next():                     
                    dauer=query.value("Dauer") 
                    errview = f"'{self.hole_movie_settings_for_dauer.__name__}': {errview} (query1)" if query.lastError().text() else errview
                else:            
                    errview = f"'{self.hole_movie_settings_for_dauer.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"keine Setting Daten für Spielzeit bei dem {baselink} gefunden")
            
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_movie_settings_for_dauer.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, dauer

    def hole_movie_settings_for_beschreibung(self, baselink: str) -> Tuple [str, str, str, str]:
        errview: str= None
        beschreibung: str= None
        beschreibung_attri: str= None
        beschreibung_clicks: str= None

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager           
            with self.managed_query() as query:
                query.prepare("SELECT Beschreibung,Beschreibung_Attri,Beschreibung_Clicks From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink)        
                query.exec()        
                if query.next():                    
                    beschreibung=query.value("Beschreibung")
                    beschreibung_attri=query.value("Beschreibung_Attri")
                    beschreibung_clicks=query.value("Beschreibung_Clicks")  
                    errview = f"'{self.hole_movie_settings_for_beschreibung.__name__}': {errview} (query1)" if query.lastError().text() else errview                    
                else:
                    errview = f"'{self.hole_movie_settings_for_beschreibung.__name__}': {errview} (query)" if query.lastError().text() else (errview or "keine Settings Daten für die Filmbeschreibung gefunden")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_movie_settings_for_beschreibung.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, beschreibung, beschreibung_attri, beschreibung_clicks 

    def get_movie_settings_for_erstelldatum(self, baselink: str) -> Tuple [str, str, str]:
        errview: str= None
        erstell_datum: str= None        
        erstell_datum_format: str= None

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager           
            with self.managed_query() as query:
                query.prepare("SELECT ReleaseDate, ReleaseDate_Format From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink)
                query.exec()        
                if query.next():
                    erstell_datum=query.value("ReleaseDate")                    
                    erstell_datum_format=query.value("ReleaseDate_Format") 
                    errview = f"'{self.get_movie_settings_for_erstelldatum.__name__}': {errview} (query1)" if query.lastError().text() else errview                   
                else:            
                    errview = f"'{self.get_movie_settings_for_erstelldatum.__name__}': {errview} (query)" if query.lastError().text() else (errview or "keine Setting Daten für das Erstelldatum gefunden")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_movie_settings_for_erstelldatum.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, erstell_datum, erstell_datum_format 
    
    def get_lastVisite(self, baselink: str) -> str: 
        errorview: str = None
        last_visite: str = None  

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager   
            with self.managed_query() as query:
                query.prepare("SELECT lastVisite FROM WebScrapping_Settings WHERE Homepage = :Link;")
                query.bindValue(":Link",baselink)
                query.exec()
                if query.next():                    
                    last_visite = query.value("lastVisite")
                    errview = f"'{self.get_lastVisite.__name__}': {errview} (query1)"  if query.lastError().text() else errview                    
                else:
                    errview = f"'{self.get_lastVisite.__name__}': {errview} (query)"  if query.lastError().text() else (errview or "kein Eintrag in der Datenbank gefunden beim letzten Side-Besuch")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_lastVisite.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errorview, last_visite

    def get_last_side_from_db(self, baselink: str) -> int:
        errview: str = None
        last_page_number: int = 2

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager   
            with self.managed_query() as query:
                query.prepare("SELECT video_last_side From WebScrapping_Settings WHERE Homepage=:link;")
                query.bindValue(":link",baselink)                          
                query.exec()        
                if query.next():
                    last_page_number = query.value("video_last_side") if isinstance(query.value("video_last_side"), int) else 2 
                    errview = f"'{self.get_last_side_from_db.__name__}': {errview} (query1)" if query.lastError().text() else errview                   
                else:
                    errview = f"'{self.get_last_side_from_db.__name__}': {errview} (query)" if query.lastError().text() else (errview or "kein Eintrag in letzte Seite gefunden")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_last_side_from_db.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, last_page_number 
        
    def get_last_side_settings(self, baselink: str) -> Tuple [str, str, str, str, str, str]: 
        errview: str = None 
        last_page: str = None 
        homepage: str = None 
        start_click: str = None 
        video_page: str = None 

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager   
            with self.managed_query() as query:
                query.prepare("SELECT last_side,last_side_attri, Homepage, WebScrapping_Settings.Click, WebScrapping_Settings.Video_page FROM Such_Infos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = Such_Infos.SettingID WHERE WebScrapping_Settings.Homepage = :Link")
                query.bindValue(":Link", baselink)
                query.exec()        
                if query.next():                    
                    last_page=query.value("last_side")
                    last_page_attri=query.value("last_side_attri")
                    homepage=query.value("Homepage")
                    start_click=query.value("WebScrapping_Settings.Click")
                    video_page=query.value("WebScrapping_Settings.Video_page") 
                    errview = f"'{self.get_last_side_settings.__name__}': {errview} (query1)" if query.lastError().text() else errview
                else:                     
                    errview = f"'{self.get_last_side_settings.__name__}': {errview} (query)" if query.lastError().text() else (errview or "keine letzte Seite gefunden")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_last_side_settings.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, last_page, last_page_attri, homepage, start_click, video_page
    
    ### ---- einzelen Daten holen für Programmstruktur ----------- ####
    def get_buttonlogo_from_studio(self, studio: str) -> Tuple[str, str, str]: 
        errview: str = None         
        logo: str  = None 

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager               
            with self.managed_query() as query: 
                query.prepare(f"SELECT WebScrapping_Settings.Name, logo From Scrap_MovieInfos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = Scrap_MovieInfos.SettingID WHERE Name = :Studio;")
                query.bindValue(":Studio", studio)
                query.exec()        
                if query.next():                    
                    studio = query.value("WebScrapping_Settings.Name") 
                    logo = query.value("logo") 
                    errview = f"'{self.get_buttonlogo_from_studio.__name__}': {errview} (query1)" if query.lastError().text() else errview                   
                else:
                    errview = f"'{self.get_buttonlogo_from_studio.__name__}': {errview} (query)" if query.lastError().text() else (errview or "kein Studio-Logo/Name gefunden")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_buttonlogo_from_studio.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, studio, logo

    def hole_verschiebe_ordner(self, studio: str) -> Tuple[str, str]:
        errview: str = None
        datei_ordner: str = None 
        
        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager           
            with self.managed_query() as query:
                query.prepare("SELECT DateiOrdner FROM Scrap_MovieInfos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = Scrap_MovieInfos.SettingID WHERE Name=:Studio;")
                query.bindValue(":Studio", studio)
                query.exec()
                if query.next():                    
                    datei_ordner = query.value("DateiOrdner")
                    errview = f"'{self.hole_verschiebe_ordner.__name__}': {errview} (query1)" if query.lastError().text() else errview
                else:
                    errview = f"'{self.hole_verschiebe_ordner.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"keinen Datei Ordner gefunden für {studio} (query)")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_verschiebe_ordner.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, datei_ordner

    ##### ------------ Überprüfungen ---------------- ######
    ########################################################   
    def is_studio_in_db(self, studio: str) -> bool:
        errview: str = None
        is_vorhanden: bool=False

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager   
            with self.managed_query() as query:
                query.prepare("SELECT Name FROM WebScrapping_Settings WHERE Name = :Studio;") 
                query.bindValue(":Studio", studio)
                query.exec()
                if query.next():
                    is_vorhanden=True
                    errview = f"'{self.is_studio_in_db.__name__}': {errview} (query1)" if query.lastError().text() else errview
                else:                     
                    errview = f"'{self.is_studio_in_db.__name__}': {errview} (query)" if query.lastError().text() else (errview or "kein Studio gefunden (query)")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.is_studio_in_db.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return is_vorhanden
    
    def from_link_to_spider(self, link: str) -> Tuple[str, str]:
        errview: str = None
        spider: str = None

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager               
            with self.managed_query() as query:                 
                query.prepare('SELECT Spider FROM Webscrapping_Settings WHERE Homepage = :BaseLink;')
                query.bindValue(":BaseLink",link)                
                query.exec()                           
                if query.next():  
                    spider = query.value("Spider")
                    errview = f"keinen Spider gefunden für {link}" if not query.lastError().text() and not spider else query.lastError().text()
                else:                                         
                    errview = f"'{self.from_link_to_spider.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"keinen Spider gefunden für {link}")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.from_link_to_spider.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return errview, spider 

    def from_link_to_studio(self, link: str) -> Tuple[str, str]:
        errview: str = None
        studio: str = None

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager               
            with self.managed_query() as query:                 
                query.prepare('SELECT Name FROM Webscrapping_Settings WHERE Homepage = :BaseLink;')
                query.bindValue(":BaseLink",link)                
                query.exec()                           
                if query.next():                
                    studio = query.value("Name")
                    errview = f"kein Studio gefunden für {link}" if not query.lastError().text() and not studio else query.lastError().text()
                else:                                         
                    errview = f"'{self.from_link_to_studio.__name__}': {errview} (query)" if query.lastError().text() else (errview or "keinen Studio gefunden")                
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.from_link_to_studio.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return errview, studio 
    
    
    def from_studio_to_all_baselinks(self, studio: str) -> Tuple[str, list]:
        errview: str = None
        links: list = []

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager               
            with self.managed_query() as query:                 
                query.prepare(f'SELECT Homepage FROM Webscrapping_Settings WHERE Name = :Studio;')
                query.bindValue(":Studio",studio)                
                query.exec()                                                                          
                while query.next():
                    links.append(query.value("Homepage"))
                    errview = f"'{self.from_studio_to_all_baselinks.__name__}': {errview} (query1)" if query.lastError().text() else errview
                errview = (errview or f"kein link gefunden für {studio}") if not query.lastError().text() and not links else query.lastError().text()               
                errview = f"'{self.from_studio_to_all_baselinks.__name__}': {errview} (query)" if errview and "kein " not in str(errview) else errview
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.from_studio_to_all_baselinks.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()       
        return errview, links
    
    def from_studio_to_subside_for_iafd(self, studio_raw: str) -> Tuple [str, str]:
        errview: str = None
        studio: str = None 
        serie: str = None 

        self.open_database()
        if self.db.isOpen(): # öffnet die datenbank mit einem contex Manager   
            with self.managed_query() as query:
                query.prepare("SELECT Name, Studio_Alias.Serie FROM WebScrapping_Settings JOIN Studio_Alias ON SettingID = Studio_Alias.SettingsID WHERE Studio_Alias.Serie_Alias = :Serie_Alias;") 
                query.bindValue(":Serie_Alias",studio_raw)
                query.exec()
                if query.next():
                    studio=query.value("Name")
                    serie=query.value("Studio_Alias.Serie")
                    errview = f"kein Studio für {studio_raw}" if not query.lastError().text() and not studio else query.lastError().text()
                else:
                    errview = f"'{self.from_studio_to_subside_for_iafd.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"kein Studio für {studio_raw}")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.from_studio_to_subside_for_iafd.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return studio, serie


if __name__ == "__main__":
    Webside_Settings()