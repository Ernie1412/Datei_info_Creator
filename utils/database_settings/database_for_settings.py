from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtCore import QDateTime
from contextlib import contextmanager
import logging
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
   
    def __init__(self, MainWindow=None):
        super().__init__() 
        self.Main = MainWindow 
        QSqlDatabase.removeDatabase('my_connection') # Vorhandene Verbindung schließen
        self.db= QSqlDatabase.addDatabase("QSQLITE",'my_connection')
        self.db.setHostName("localhost")
        self.db.setDatabaseName(SETTINGS_DB_PATH) 
    
    @contextmanager
    def managed_query(self):
        query = QSqlQuery(self.db)
        try:
            yield query
        finally:
            del query
    ##### ------------ Fehler-Behandlung ---------------- ##########
    ################################################################
    def db_fehler(self,von_welchen_feld: str, db_or_query) -> None:
        fehler: str = None      
        if isinstance(db_or_query, str): 
            fehler=db_or_query
        else:
            fehler=db_or_query.lastError().text()        
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.Main.lbl_db_status.setStyleSheet("background-color : #FA5882")
        self.Main.lbl_db_status.setText(f"Zeit: {current_time} --> Fehler: {fehler} - >{von_welchen_feld}<")   


    ##### ------------ speichere/adde Datenpaket(e) ---------------- ##########
    ###########################################################################
    def add_lastVisite(self, lastVisite: str, studio: str, Page_onSide: str=None) -> None:
        self.db.open()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("UPDATE WebScrapping_Settings SET lastVisite = :lastVisite, Page_onSide = COALESCE(:Page_onSide,Page_onSide) WHERE Name = :Name;")
                query.bindValue(":lastVisite",lastVisite)
                query.bindValue(":Name",studio)
                query.bindValue(":Page_onSide",Page_onSide)                
                query.exec()                
        else:
            self.db_fehler("Fehler beim Speichern des letzte Side Besuchs (db)",self.db)
        self.db.close()

    def addArtistInfos(self,studio_low,Studio,logo,DateiOrdner,Film,Film_Attri,WebSide,Regie,Artist,Artist_Attri,Artist_Single,Artist_Sleep,Artist_Gross,Artist_Sex,ErstellDatum,ErstellDatum_Art,NebenSide,NebenSide_Attri,Beschreibung,Beschreibung_Attri,Beschreibung_Clicks,Tags,Tags_Attri,Tags_Clicks,Tags_Sleep,Tags_Gross,Titel,Titel_Attri):
        logging.basicConfig(filename='my_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.db.open() 
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT SettingID FROM WebScrapping_Settings WHERE Name = :Name;")
                query.bindValue(":Name",Studio)
                query.exec()        
                if query.next():
                    setting_id=query.value("SettingID")  
                with self.managed_query() as query:      
                    query.prepare("INSERT INTO Scrap_MovieInfos (ArtistID, pornside_low,  SettingID,  logo, DateiOrdner, WebSide,Film,Film_Attri,\
                        Regie, Artist, Artist_Attri, Artist_Single, Artist_Sleep, Artist_Gross, Artist_Sex, ReleaseDate, ReleaseDate_Art, NebenSide, \
                        NebenSide_Attri, Beschreibung, Beschreibung_Attri, Beschreibung_Clicks, Tags, Tags_Attri, Tags_Clicks, Tags_Sleep, Tags_Gross,\
                        Titel, Titel_Attri) VALUES (NULL, :pornside_low, :SettingID, :logo, :DateiOrdner, :WebSide, :Film,:Film_Attri, :Regie, :Artist, \
                        :Artist_Attri, :Artist_Single, :Artist_Sleep, :Artist_Gross, :Artist_Sex, :ReleaseDate, :ReleaseDate_Art, :NebenSide, \
                        :NebenSide_Attri, :Beschreibung, :Beschreibung_Attri, :Beschreibung_Clicks, :Tags, :Tags_Attri, :Tags_Clicks, :Tags_Sleep, \
                        :Tags_Gross, :Titel, :Titel_Attri)")
                    query.bindValue(":pornside_low", studio_low)
                    query.bindValue(":logo", logo)
                    query.bindValue(":DateiOrdner", DateiOrdner)
                    query.bindValue(":Film", Film)
                    query.bindValue(":Film_Attri", Film_Attri)
                    query.bindValue(":WebSide", WebSide)
                    query.bindValue(":Regie", Regie)
                    query.bindValue(":Artist", Artist)
                    query.bindValue(":Artist_Attri", Artist_Attri)
                    query.bindValue(":ReleaseDate", ErstellDatum)
                    query.bindValue(":NebenSide", NebenSide)
                    query.bindValue(":NebenSide_Attri", NebenSide_Attri)
                    query.bindValue(":Beschreibung", Beschreibung)
                    query.bindValue(":Beschreibung_Attri", Beschreibung_Attri)
                    query.bindValue(":Beschreibung_Clicks", Beschreibung_Clicks)
                    query.bindValue(":Tags", Tags)
                    query.bindValue(":Tags_Attri", Tags_Attri)
                    query.bindValue(":Tags_Clicks", Tags_Clicks)
                    query.bindValue(":Titel", Titel)
                    query.bindValue(":Titel_Attri", Titel_Attri)
                    query.bindValue(":SettingID", int(setting_id))
                    query.bindValue(":Artist_Single", int(Artist_Single))
                    query.bindValue(":Artist_Sleep", int(Artist_Sleep))
                    query.bindValue(":Artist_Gross", int(Artist_Gross))
                    query.bindValue(":Artist_Sex", int(Artist_Sex))
                    query.bindValue(":ReleaseDate_Art", int(ErstellDatum_Art))
                    query.bindValue(":Tags_Sleep", int(Tags_Sleep))
                    query.bindValue(":Tags_Gross", int(Tags_Gross))         
                    query.exec()        
        else:
            self.db_fehler()
        self.db.close()
    ##### ------------ updates von Datenpakete ---------------- ######
    ##################################################################
    def update_letzte_seite(self, baselink: str, last_page_number: str) -> str: 
        errorview: str = None

        self.db.open()            
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("UPDATE WebScrapping_Settings SET video_last_side = :video_last_side WHERE Homepage = :Link;")
                query.bindValue(":Link",baselink)
                query.bindValue(":video_last_side",last_page_number)                
                query.exec() 
                errorview = query.lastError().text()               
        else:
            self.db_fehler("Fehler beim updaten/speichern der letzten Side-Page anhand des Baselinks (db)",self.db)
        self.db.close()
        return errorview  
    
    ##### ------------ hole ganze Datenpakete ---------------- ######
    #################################################################
    def hole_suchinfos(self,studio):   ### muss überarbeitet werden !!!
        errview: str = None
        self.db.open()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare(f"SELECT ViewAll,WebScrapping_Settings.last_side,WebScrapping_Settings.ein_weiter,WebScrapping_Settings.Artist_page,\
                              Maske,Artist,Artist_Attri,Artist_Gross,Titel,Titel_Attri,Link,Link_Attri,Link_Single,Image,Such_Infos.Image_Attri,\
                              Such_Infos.Image_Wordcut,Such_Infos.Image_Single,Dauer,Dauer_Attri,Dauer_Single,ReleaseDate,ReleaseDate_Attri,NebenSide,\
                              NebenSide_Attri FROM Such_Infos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = \
                              Such_Infos.SettingID WHERE Name='{studio}';")
                query.exec()        
                if query.next():
                    last_page=query.value("WebScrapping_Settings.last_side")                
                    Set_Artist_page=query.value("WebScrapping_Settings.Artist_page")
                    ein_weiter=query.value("WebScrapping_Settings.ein_weiter")
                    ViewAll=query.value("ViewAll")
                    Maske=query.value("Maske")                
                    Artist=query.value("Artist")
                    Artist_Attri=query.value("Artist_Attri")                    
                    Artist_Gross=query.value("Artist_Gross")  
                    Titel=query.value("Titel") 
                    Titel_Attri=query.value("Titel_Attri")                
                    Link=query.value("Link") 
                    Link_Attri=query.value("Link_Attri")
                    Link_Single=query.value("Link_Single")  
                    Image=query.value("Image") 
                    Image_Attri=query.value("Image_Attri")
                    Image_Wordcut=query.value("Image_Wordcut") 
                    Image_Single=query.value("Image_Single")
                    Dauer=query.value("Dauer")
                    Dauer_Attri=query.value("Dauer_Attri") 
                    Dauer_Single=query.value("Dauer_Single")
                    ReleaseDate=query.value("ReleaseDate") 
                    ReleaseDate_Attri=query.value("ReleaseDate_Attri")  
                    NebenSide=query.value("NebenSide") 
                    NebenSide_Attri=query.value("NebenSide_Attri")                        
                else:                     
                    ViewAll,last_page,ein_weiter,Set_Artist_page,Maske,Artist,Artist_Attri,Artist_Gross,Titel,Titel_Attri,Link,Link_Attri,\
                    Link_Single,Image,Image_Attri,Image_Wordcut,Image_Single,Dauer,Dauer_Attri,Dauer_Single,ReleaseDate,ReleaseDate_Attri,\
                    NebenSide,NebenSide_Attri=(query.lastError().text(),"","","","","","",0,"","",0,"","",0,"","","",0,"","",0,"","","","") 
        else:
            self.db_fehler("Fehler beim holen von Settings für Webscrapings anhand des Studionamens (db)",self.db)
        self.db.close()
        return ViewAll,last_page,ein_weiter,Set_Artist_page,Maske,Artist,Artist_Attri,Artist_Gross,Titel,Titel_Attri,Link,Link_Attri,\
                Link_Single,Image,Image_Attri,Image_Wordcut,Image_Single,Dauer,Dauer_Attri,Dauer_Single,ReleaseDate,ReleaseDate_Attri,\
                NebenSide,NebenSide_Attri 
    
    def get_videodatas_from_baselink(self, link: str) -> str:              
        errorview: str = None
        settings_data = SettingsData()

        self.db.open()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT * FROM Such_Infos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = Such_Infos.SettingID WHERE Homepage=:Homepage")
                query.bindValue(":Homepage",link)
                query.exec()        
                if query.next():                    
                    video_data = settings_data.initialize(query.record())
                    errorview = query.lastError().text()
                else:
                    errorview = "keine Daten für Video-Settings gefunden"
        else:
            self.db_fehler("Fehler beim holen von Video-Daten anhand von Baselink (db)",self.db)
        self.db.close()        
        return errorview, settings_data
    
    ##### ------------ hole einzelne Daten ---------------- ######
    ##############################################################
    def query_hole_settings_artist(self, studio): ### muss überarbeit werden ! ###
        query = self.managed_query()
        query.prepare("SELECT * FROM WebScrapping_Settings WHERE Name=:Name;")
        query.bindValue(":Name", studio)
        query.exec()
        return query ### muss überarbeit werden ! ###
    
    def hole_settings_artist(self, studio: str) -> Tuple [str, dict]:
        errorview: str = None         
        settings_data = SettingsData()

        self.db.open()        
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT * From WebScrapping_Settings WHERE Name = :Studio;")
                query.bindValue(":Studio", studio) 
                if query.next():
                    video_data = settings_data.initialize(query.record())
                    errorview = query.lastError().text()
                else:
                    errorview = "keine Daten für Artist"
        else:
            self.db_fehler("Fehler beim Performer Settings holen (db)",self.db) 
        self.db.close()
        return errorview, video_data
    
    def get_movie_settings_for_titel(self, baselink: str) -> Tuple [str, str, str]:  ### funktion noch nicht in Benutzung ###
        errview: str = None
        titel: str = None 
        titel_attri: str = None

        self.db.open()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT Titel, Titel_Attri From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink)
                query.exec()        
                if query.next(): 
                    titel=query.value("Titel")
                    titel_attri=query.value("Titel_Attri") 
                    errview = query.lastError().text()              
                else:
                    errview = "kein Titel Daten gefunden"
        else:
            self.db_fehler("Fehler beim holen von Titel-Settings (db)",self.db)
        self.db.close()
        return errview, titel, titel_attri    

    def get_movie_settings_for_tags(self, baselink: str) -> Tuple [str, str, str]:
        errview: str= None
        tags: str = None
        tags_attri: str = None
        tags_click: str = None

        self.db.open()
        if self.db.isOpen():
            with self.managed_query() as query:            
                query.prepare("SELECT Tags, Tags_Attri, Tags_Clicks FROM Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink) 
                query.exec()        
                if query.next():
                    tags = query.value("Tags")
                    tags_attri = query.value("Tags_Attri")
                    tags_click = query.value("Tags_Clicks")                    
                    errview = query.lastError().text()
                else:            
                    errview = "keine Daten gefunden"
        else:
            self.db_fehler("Fehler beim holen von Tags-Settings (db)",self.db)
        self.db.close()
        return errview, tags, tags_attri, tags_click    

    def hole_movie_settings_for_artist(self, baselink: str) -> Tuple [str, list]:
        errview: str= None
        artist: str= None
        artist_gross: str= None

        self.db.open()
        if self.db.isOpen():       
            with self.managed_query() as query:
                query.prepare("SELECT Artist, Artist_Gross From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink) 
                query.exec()        
                if query.next(): 
                    artist=query.value("Artist")                    
                    artist_gross=query.value("Artist_Gross")
                    errorview = query.lastError().text()                  
                else:            
                    errorview = "keine Setting Daten für Performers gefunden"
        else:
            self.db_fehler("Fehler beim holen von Performer-Settings (db)",self.db)
        self.db.close()
        return errview, artist, artist_gross

    def hole_movie_settings_for_nebenside(self, baselink: str) -> Tuple [str, str, str]:
        errview: str= None
        nebenside: str= None        

        self.db.open()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT NebenSide FROM Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink)
                query.exec()
                if query.next(): 
                    nebenside=query.value("NebenSide")                    
                    errview = query.lastError().text()                   
                else:            
                    errview = "keine Setting daten für Serie, Nebensides gefunden"
        else:
            self.db_fehler("Fehler beim holen von Sub-Side/Serie (db)",self.db)
        self.db.close()
        return errview, nebenside

    def hole_movie_settings_for_dauer(self, baselink: str) -> Tuple [str, str]:
        errview: str= None
        dauer: str= None        

        self.db.open() 
        if self.db.isOpen():       
            with self.managed_query() as query:
                query.prepare("SELECT Dauer From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink) 
                query.exec()        
                if query.next(): 
                    dauer=query.value("Dauer")                    
                    errview = query.lastError().text()                    
                else:            
                    errview = "keine Setting Daten für Spielzeit gefunden"
        else:
            self.db_fehler("Fehler beim holen von Runtime (db)",self.db)
        self.db.close()
        return errview, dauer

    def hole_movie_settings_for_beschreibung(self, baselink: str) -> Tuple [str, str, str, str]:
        errview: str= None
        beschreibung: str= None
        beschreibung_attri: str= None
        beschreibung_clicks: str= None

        self.db.open()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT Beschreibung,Beschreibung_Attri,Beschreibung_Clicks From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink)        
                query.exec()        
                if query.next(): 
                    beschreibung=query.value("Beschreibung")
                    beschreibung_attri=query.value("Beschreibung_Attri")
                    beschreibung_clicks=query.value("Beschreibung_Clicks")
                    errview = query.lastError().text() 
                else:
                    errview = "keine Settings Daten für die Filmbeschreibung gefunden"
        else:
            self.db_fehler("Fehler beim holen von Beschreibung/Synopsis (db)",self.db)
        self.db.close()
        return errview, beschreibung, beschreibung_attri, beschreibung_clicks 

    def get_movie_settings_for_erstelldatum(self, baselink: str) -> Tuple [str, str, str]:
        errview: str= None
        erstell_datum: str= None        
        erstell_datum_format: str= None

        self.db.open()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT ReleaseDate, ReleaseDate_Format From Scrap_MovieInfos WHERE WebSide=:link;")
                query.bindValue(":link", baselink)
                query.exec()        
                if query.next(): 
                    erstell_datum=query.value("ReleaseDate")                    
                    erstell_datum_format=query.value("ReleaseDate_Format")
                    errview = query.lastError().text()
                else:            
                    errview = "keine Setting Daten für das Erstelldatum gefunden"
        else:
            self.db_fehler("Fehler beim holen von Release-Datum (db)",self.db)
        self.db.close()
        return errview, erstell_datum, erstell_datum_format 
    
    def get_lastVisite(self, baselink: str) -> str: 
        errorview: str = None
        last_visite: str = None  

        self.db.open()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT lastVisite FROM WebScrapping_Settings WHERE Homepage = :Link;")
                query.bindValue(":Link",baselink)
                query.exec()
                if query.next():
                    last_visite = query.value("lastVisite")
                    errorview = query.lastError().text()
                else:
                    errorview = "kein Eintrag in der Datenbank gefunden beim letzten Side-Besuch"
        else:
            self.db_fehler("Fehler beim Laden des letzte Side Besuchs (db)",self.db)
        self.db.close()
        return errorview, last_visite

    def get_last_side_from_db(self, baselink: str) -> int:
        errorview: str = None
        last_page_number: int = 2

        self.db.open()        
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT video_last_side From WebScrapping_Settings WHERE Homepage=:link;")
                query.bindValue(":link",baselink)                          
                query.exec()        
                if query.next(): 
                    last_page_number = query.value("video_last_side") if isinstance(query.value("video_last_side"), int) else 2
                    errorview = query.lastError().text()
                else:
                    errorview = "kein Eintrag in letzte Seite gefunden"
        else:
            self.db_fehler("Fehler beim Laden des letzte Side Page (db)",self.db)
        self.db.close()
        return errorview, last_page_number 
        
    def get_last_side_settings(self, baselink: str) -> Tuple [str, str, str, str, str, str]: 
        errview: str = None 
        last_page: str = None 
        homepage: str = None 
        start_click: str = None 
        video_page: str = None 

        self.db.open()            
        if self.db.isOpen():
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
                    errorview = query.lastError().text()
                    if errorview:
                        self.db_fehler("Fehler beim Holen der letzten Side-Page (query)",query)                  
                else:                     
                    errorview = "keine letzte Seite gefunden" 
        else:
            self.db_fehler("Fehler beim Holen der letzten Side-Page (db)",self.db)
        self.db.close()
        return errview, last_page, last_page_attri, homepage, start_click, video_page
    
    ### ---- einzelen Daten holen für Programmstruktur ----------- ####
    def get_buttonlogo_from_studio(self, studio: str) -> Tuple[str, str, str]: 
        start_seite: str = None 
        logo: str  = None 
        start_seite: str  = None
        errorview: str = None 

        self.db.open()            
        if self.db.isOpen():            
            with self.managed_query() as query: 
                query.prepare(f"SELECT WebScrapping_Settings.Name, logo From Scrap_MovieInfos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = Scrap_MovieInfos.SettingID WHERE Name = :Studio;")
                query.bindValue(":Studio", studio)
                query.exec()        
                if query.next():
                    studio = query.value("WebScrapping_Settings.Name") 
                    logo = query.value("logo")
                    errorview = query.lastError().text()
                    if errorview:
                        self.db_fehler("Fehler beim Studio-logo holen (query)",query) 
                else:
                    errorview = "keine Web-Infos gefunden" 
        else:
            self.db_fehler("Fehler beim Studio-logo holen (db)",self.db)
        self.db.close()
        return errorview, studio, logo

    def hole_verschiebe_ordner(self, studio: str) -> Tuple[str, str]:
        errview: str = None
        DateiOrdner: str = None 
        
        self.db.open()  
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT DateiOrdner FROM Scrap_MovieInfos INNER JOIN WebScrapping_Settings ON WebScrapping_Settings.SettingID = Scrap_MovieInfos.SettingID WHERE Name=:Studio;")
                query.bindValue(":Studio", studio)
                query.exec()
                if query.next():
                    DateiOrdner = query.value("DateiOrdner")
                else:
                    if not query.lastError().text():
                        errview = "Keine Daten gefunden."
                    else:
                        errview = "Ein Datenbankfehler ist aufgetreten: " + query.lastError().text()
        else:
            self.db_fehler("Fehler beim holen von Verschiebe-Ordner (db)",self.db)
        return errview, DateiOrdner

    ##### ------------ Überprüfungen ---------------- ######
    ########################################################   
    def is_studio_in_db(self, studio: str) -> str:
        self.db.open()  
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT Name FROM WebScrapping_Settings WHERE Name = :Studio;") 
                query.bindValue(":Studio", studio)
                query.exec()
                if not query.next():
                    studio = None 
        else:
            self.db_fehler("Fehler beim Überprüfen des Studionamens (db)",self.db)
        self.db.close()
        return studio
    
    def from_link_to_spider(self, link: str) -> Tuple[str, str]:
        errorview: str = None
        spider: str = None

        self.db.open()            
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare('SELECT Spider FROM Webscrapping_Settings WHERE Homepage = :BaseLink;')
                query.bindValue(":BaseLink",link)                
                query.exec()                           
                if query.next():
                    if query.lastError().text():
                        errorview = query.lastError().text()
                        self.db_fehler("von Link zum Spider Überprüfung (query)",query)
                    else:
                        spider = query.value("Spider")
                        if not spider:
                            errorview = "kein Eintrag gefunden !"
                else:
                    errorview = "kein Eintrag gefunden !"
        else:
            self.db_fehler("von Link zum Spider Überprüfung (db)",self.db)
        self.db.close()        
        return errorview, spider  
    
    
    def from_studio_to_all_baselinks(self, studio: str) -> Tuple[str, list]:
        errorview: str = None
        links: list = []

        self.db.open()            
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare(f'SELECT Homepage FROM Webscrapping_Settings WHERE Name = :Studio;')
                query.bindValue(":Studio",studio)                
                query.exec()                                                                          
                while query.next():
                    if query.lastError().text():
                        self.db_fehler("von Links holen mit Hilfe von Studionamen (query)",query)
                        
                    links.append(query.value("Homepage"))
                errorview = query.lastError().text()
        else:
            self.db_fehler("von Links holen mit Hilfe von Studionamen (db)",self.db)
        self.db.close()        
        return errorview, links
    
    def from_studio_to_subside_for_iafd(self, studio_raw: str) -> Tuple [str, str]:
        studio: str = None 
        serie: str = None 
        self.db.open()  
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT Name, Studio_Alias.Serie FROM WebScrapping_Settings JOIN Studio_Alias ON SettingID = Studio_Alias.SettingsID WHERE Studio_Alias.Serie_Alias = :Serie_Alias;") 
                query.bindValue(":Serie_Alias",studio_raw)
                query.exec()
                if query.next():
                    studio=query.value("Name")
                    serie=query.value("Studio_Alias.Serie")
                else:
                    errorview = query.lastError().text()
        else:
            self.db_fehler("Fehler beim SubSide holen in Alias Tabelle (db)",self.db)
        self.db.close()
        return studio, serie


if __name__ == "__main__":
    Webside_Settings()