from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtCore import QDateTime
from contextlib import contextmanager
from typing import Tuple, Optional

from config import PERFORMER_DB_PATH
from utils.database_settings.database_for_scrapings import VideoData


class DB_Darsteller:

    def __init__(self, MainWindow=None):
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
            del query

    def open_database(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE",'db_darsteller')
        self.db.setHostName("localhost")        
        self.db.setDatabaseName(PERFORMER_DB_PATH)
        self.db.open()
    
    def close_database(self):
        self.db.close()            
        connection_name = self.db.connectionName()
        del self.db
        QSqlDatabase.database(connection_name).close()         
        QSqlDatabase.removeDatabase(connection_name) # Vorhandene Verbindung schließen

    def db_fehler(self,fehler: str) -> None:
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        if fehler.startswith("kein"):
            self.Main.lbl_db_status.setStyleSheet("background-color : #FFCB8F")
        else:
            self.Main.lbl_db_status.setStyleSheet("background-color : #FA5882")
        self.Main.lbl_db_status.setText(f"{current_time} --> {fehler}")

    ############################################################################################ 
    ###------------------------ Daten in der Datenbank überprüfen -------------------------- ###
    ############################################################################################ 
    def isdaDarsteller(self, name: str, studio: str=None) -> Tuple[bool, int]:
        errview: Optional[str]=None
        is_vorhanden: bool=False
        sex: int = 0
        
        self.open_database()
        if self.db.isOpen():                              
            command = "SELECT Geschlecht FROM DB_Artist WHERE Name = :Performername"
            if studio:
                command += " AND ArtistID IN (SELECT ArtistID FROM DB_NamesLink INNER JOIN Studios ON DB_NamesLink.StudioID = \
                            Studios.StudioID WHERE StudioName = :studio)"
            with self.managed_query() as query:
                query.prepare(command)
                query.bindValue(":Performername", name)
                query.bindValue(":studio", studio)
                query.exec()       
                if query.next():                    
                    sex = query.value("Geschlecht")                       
                    is_vorhanden = True
                    errview = query.lastError().text() if query.lastError().text() else None
                else:
                    errview = f"'{self.isdaDarsteller.__name__}': kein {name} gefunden in der Datenbank" if not query.lastError().text() else f"'{self.isdaDarsteller.__name__}': {query.lastError().text()} (query)"                    
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.isdaDarsteller.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return is_vorhanden, sex 
    ### --------------------------- Nationen --------------------------- ####
    def get_nation_eng_to_german(self, nation_eng):
        errview: str=None
        nation_ger: str=None        

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT NationVolk_GER FROM Nationen WHERE NationVolk_ENG = :nation_eng;")
                query.bindValue(":nation_eng", nation_eng)                               
                query.exec()       
                if query.next():                    
                    nation_ger = query.value("NationVolk_GER") 
                    errview =  f"'{self.get_nation_eng_to_german.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:
                    err_text = query.lastError().text()
                    errview = f"'{self.get_nation_eng_to_german.__name__}': kein '{nation_eng}' gefunden in der Datenbank" if not err_text else f"'{self.get_nation_eng_to_german.__name__}': {err_text} (query)"
                                        
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_nation_eng_to_german.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return nation_ger

    def get_nations_id_from_nations_ger(self, nations_ger: str) -> int:
        errview: str=None
        nations_id: int=-1     

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT NationID FROM Nationen WHERE NationVolk_GER = :NationVolk_GER;")  
                query.bindValue(":NationVolk_GER", nations_ger)                                             
                query.exec()       
                if query.next(): 
                    nations_id=query.value("NationID")
                    errview = f"'{self.get_nations_id_from_nations_ger.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:                    
                    errview = f"'{self.get_nations_id_from_nations_ger.__name__}': kein '{nations_ger}' gefunden in der Datenbank" if nations_id == -1 else f"'{self.get_nations_id_from_nations_ger.__name__}': {query.lastError().text()} (query)"
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_nations_id_from_nations_ger.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return nations_id

    def get_nation_ger_to_english(self, nation_ger):
        errview: str=None
        nation_eng: str=None        

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT NationVolk_ENG FROM Nationen WHERE NationVolk_GER = :nation_ger;")
                query.bindValue(":nation_ger", nation_ger)                               
                query.exec()       
                if query.next():                    
                    nation_eng = query.value("NationVolk_ENG") 
                    errview =  f"'{self.get_nation_ger_to_english.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:
                    err_text = query.lastError().text()
                    errview = f"'{self.get_nation_ger_to_english.__name__}': kein '{nation_eng}' gefunden in der Datenbank" if not err_text else f"'{self.get_nation_eng_to_german.__name__}': {err_text} (query)"
                                        
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_nation_ger_to_english.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return nation_eng
    
    def get_shortsymbol_from_german(self, nation_ger):
        errview: str=None
        shortsymbol: str=None        

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT Kuerzel FROM Nationen WHERE NationVolk_GER = :nation_ger;")
                query.bindValue(":nation_ger", nation_ger)                               
                query.exec()       
                if query.next():                    
                    shortsymbol = query.value("Kuerzel") 
                    errview =  f"'{self.get_nation_ger_to_english.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:
                    err_text = query.lastError().text()
                    errview = f"'{self.get_nation_ger_to_english.__name__}': kein '{shortsymbol}' gefunden in der Datenbank" if not err_text else f"'{self.get_nation_eng_to_german.__name__}': {err_text} (query)"
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_nation_ger_to_english.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return shortsymbol
    
    def get_all_nations_ger(self):
        errview: str=None
        nations: list=[]     

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT NationVolk_GER FROM Nationen;")                                               
                query.exec()       
                while query.next():                    
                    nations.append(query.value("NationVolk_GER")) 
                errview =  f"'{self.get_all_nations_ger.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_all_nations_ger.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return nations

    def get_all_nations_kuerzel(self):
        errview: str=None
        kuerzel: list=[]     

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT Kuerzel FROM Nationen;")                                               
                query.exec()       
                while query.next():                    
                    kuerzel.append(query.value("Kuerzel")) 
                errview =  f"'{self.get_all_nations_kuerzel.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_all_nations_kuerzel.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return kuerzel
    
    def get_nation_kuerzel_from_nation_ger(self, nation_ger):
        errview: str=None
        kuerzel: str=None

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT Kuerzel FROM Nationen WHERE NationVolk_GER = :nation_ger;")
                query.bindValue(":nation_ger", nation_ger)
                query.exec()
                if query.next():
                    kuerzel = query.value("Kuerzel")
                    errview =  f"'{self.get_nation_kuerzel_from_nation_ger.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:
                    err_text = query.lastError().text()
                    errview = f"'{self.get_nation_kuerzel_from_nation_ger.__name__}': kein '{kuerzel}' gefunden in der Datenbank" if not err_text else f"'{self.get_nation_kuerzel_from_nation_ger.__name__}': {err_text} (query)"
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_nation_kuerzel_from_nation_ger.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return kuerzel
    ### --------------------------- Studio --------------------------- ####
    def get_studio_id_from_baselink(self, studio_link: str) -> int:
        errview: str=None
        studio_id: int=-1       

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT StudioID FROM Studios WHERE Homepage = :studio_link;")
                query.bindValue(":studio_link", studio_link)                               
                query.exec()       
                if query.next():                    
                    studio_id = query.value("StudioID") 
                    errview =  f"'{self.get_studio_id_from_baselink.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:
                    errview = f"'{self.get_studio_id_from_baselink.__name__}': kein '{studio_link}' gefunden in der Datenbank" if not query.lastError().text() else f"'{self.get_studio_id_from_baselink.__name__}': {query.lastError().text()} (query)"
                                        
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_studio_id_from_baselink.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return studio_id
    ### --------------------------- NamesLink --------------------------- ####
    def get_namesid_from_nameslink(self, link: str) -> int:
        names_id: int=-1 
        errview: str=None             

        self.open_database()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT NamesID FROM DB_NamesLink WHERE Link = :Link;")   
                query.bindValue(":Link",link)
                query.exec()
                if query.next():
                    names_id = query.value("NamesID") 
                    errview = f"'{self.get_namesid_from_nameslink.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else errview
                else:
                    errview = f"'{self.get_namesid_from_nameslink.__name__}': kein '{names_id}' gefunden in NamesLink" if not query.lastError().text() else f"'{self.get_namesid_from_nameslink.__name__}': {query.lastError().text()} (query)"    
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_namesid_from_nameslink.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return names_id
    
    def get_nameslink_dataset_from_artistid(self, artist_id: int) -> dict:
        daten_satz: list={}
        errview: str=None             

        self.open_database()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT NamesID, Link, Image, Alias FROM DB_NamesLink JOIN DB_Artist ON DB_Artist.ArtistID=DB_NamesLink.ArtistID WHERE DB_Artist.ArtistID = :ArtistID;")   
                query.bindValue(":ArtistID",artist_id)
                query.exec()
                if query.next():
                    daten_satz={"NamesID": query.value("NamesID"),
                                "Link": query.value("Link"),
                                "Image": query.value("Image"),                        
                                "Alias": query.value("Alias"),
                                "ArtistID": artist_id}
                    errview = f"'{self.get_nameslink_dataset_from_artistid.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else errview
                else:
                    errview = f"'{self.get_nameslink_dataset_from_artistid.__name__}': kein '{artist_id}' gefunden in NamesLink" if not query.lastError().text() else f"'{self.get_nameslink_dataset_from_artistid.__name__}': {query.lastError().text()} (query)"    
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_nameslink_dataset_from_artistid.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return daten_satz

    def get_nameslink_dataset_from_namesid(self, names_id: int) -> int:
        daten_satz: list=[] 
        errview: str=None             

        self.open_database()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT NamesID, Link, Image, Alias FROM DB_NamesLink WHERE NamesID = :NamesID;")   
                query.bindValue(":NamesID",names_id)
                query.exec()
                if query.next():
                    daten_satz=[
                        query.value("NamesID"),
                        query.value("Link"),
                        query.value("Image"),                        
                        query.value("Alias"),   ]
                    errview = f"'{self.get_nameslink_dataset_from_namesid.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else errview
                else:
                    errview = f"'{self.get_nameslink_dataset_from_namesid.__name__}': kein '{names_id}' gefunden in NamesLink" if not query.lastError().text() else f"'{self.get_nameslink_dataset_from_namesid.__name__}': {query.lastError().text()} (query)"    
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_nameslink_dataset_from_namesid.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return daten_satz
    
    def get_artistid_from_nameslink(self, nameslink: str) -> int:
        artist_id: int=-1
        errview: str=None
        self.open_database()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT DB_Artist.ArtistID FROM DB_NamesLink JOIN DB_Artist ON DB_Artist.ArtistID=DB_NamesLink.ArtistID WHERE DB_NamesLink.Link = :Link;")   
                query.bindValue(":Link",nameslink)                
                query.exec()
                if query.next():
                    artist_id = query.value("DB_Artist.ArtistID") 
                    errview = f"'{self.get_artistid_from_nameslink.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:
                    errview = f"'{self.get_artistid_from_nameslink.__name__}': kein '{artist_id}' gefunden in DB_Artist" if not query.lastError().text() else f"'{self.get_artistid_from_nameslink.__name__}': {query.lastError().text()} (query)"    
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_artistid_from_name_ordner.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return artist_id
    
    ### --------------------------- Name --------------------------- ####
    def get_name_from_id(self, artist_id: int) -> str:
        name: str=None
        errview: str=None             

        self.open_database()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT Name FROM DB_Artist WHERE ArtistID = :ArtistID;")   
                query.bindValue(":ArtistID",artist_id)
                query.exec()
                if query.next():
                    name = query.value("Name") 
                    errview = f"'{self.get_name_from_id.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else errview
                else:
                    errview = f"'{self.get_name_from_id.__name__}': kein '{artist_id}' gefunden in DB_Artist" if not query.lastError().text() else f"'{self.get_name_from_id.__name__}': {query.lastError().text()} (query)"    
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_name_from_id.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return name
    ### --------------------------- Ordner --------------------------- ####
    def get_artistid_from_name_ordner(self, name: str, ordner: str) -> int:
        artist_id: int=-1
        errview: str=None 
        self.open_database()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT ArtistID FROM DB_Artist WHERE Name = :Name AND Ordner = :Ordner;")   
                query.bindValue(":Name",name)
                query.bindValue(":Ordner",ordner)
                query.exec()
                if query.next():
                    artist_id = query.value("ArtistID") 
                    errview = f"'{self.get_artistid_from_name_ordner.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else errview
                else:
                    errview = f"'{self.get_artistid_from_name_ordner.__name__}': kein '{artist_id}' gefunden in DB_Artist" if not query.lastError().text() else f"'{self.get_artistid_from_name_ordner.__name__}': {query.lastError().text()} (query)"    
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_artistid_from_name_ordner.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return artist_id   
    
    def get_all_datas_from_database(self, performers: str, page_number: int=1) -> str:
        errview: str = None 
        page_size: int = 10000
        offset = (page_number - 1) * page_size
        artist_data = VideoData()
        ### ---------------- database ---------------- ###
        self.open_database()
        if self.db.isOpen():
            ### ------------ totale Anzahl der Suchanfrage ermitteln ------------------ ###
            with self.managed_query() as query:
                query.prepare("SELECT COUNT(*) FROM DB_Artist WHERE Name LIKE :Name;")
                query.bindValue(":Name", performers)
                query.exec()                
                if query.next():
                    total_entries = query.value(0)
                    max_pages = (total_entries + page_size - 1) // page_size  # Berechnung der maximalen Seitenanzahl
                    self.Main.lnEdit_maxpage.setText(f"{max_pages}")
                else:
                    errview = f"Fehler beim Abrufen der Gesamtanzahl der Einträge: {query.lastError().text()}"
            ### ------------ eigentliche Suchanfrage ------------------ ###
            with self.managed_query() as query:
                query.prepare(f"SELECT * FROM DB_Artist WHERE Name LIKE :Name LIMIT :Limit OFFSET :Offset;")
                query.bindValue(":Name", performers)
                query.bindValue(":Limit", page_size)
                query.bindValue(":Offset", offset)
                query.exec()                
                while query.next():                                        
                    artist_data.initialize(query.record()) 
                    artist_id=query.value("ArtistID")
                    errview = f"'{self.get_all_datas_from_database.__name__}': {errview} (query1)" if query.lastError().text() else errview
                    ### ------------ Nationen Suchanfrage ------------------ ###
                    with self.managed_query() as query1:
                        query1.prepare("SELECT NationVolk_GER FROM Person_Nation JOIN Nationen ON Nationen.NationID=Person_Nation.NationID WHERE ArtistID=:ArtistID")
                        query1.bindValue(":ArtistID", artist_id)
                        query1.exec() 
                        nation_list = []               
                        while query1.next():                            
                            nation_list.append(query1.value("NationVolk_GER"))
                            errview = f"'{self.get_all_datas_from_database.__name__}': {errview} (query2)" if query.lastError().text() else errview 
                        nations=", ".join(nation_list)
                    ### ------------ Rassen Suchanfrage ------------------ ###
                    with self.managed_query() as query1:
                        query1.prepare("SELECT Rasse_ger FROM Person_Rasse JOIN Rassen ON Rassen.RassenID=Person_Rasse.RassenID WHERE ArtistID=:ArtistID")
                        query1.bindValue(":ArtistID", artist_id)
                        query1.exec() 
                        rasse_list = []               
                        while query1.next():                            
                            rasse_list.append(query1.value("Rasse_ger"))
                            errview = f"'{self.get_all_datas_from_database.__name__}': {errview} (query2)" if query.lastError().text() else errview 
                        rasse_ger = "/".join(rasse_list)  
                    data=artist_data.get_data() # daten aus der Klasse bekommen, ansonsten nur eine Speicheradresse                                                
                    data[len(data)-1]["Nation"]=nations # "Nation" wird dem letzten 'index' '(len(data)-1)' hinzugefügt
                    data[len(data)-1]["Rassen"]=rasse_ger # "Rasse_ger" wird dem letzten '
                    artist_data.save_data(data) # speichert die bearbeiteten Daten in die Klasse wieder rein                                               
                    del query1
                errview = (errview or f"kein {performers} gefunden") if not query.lastError().text() and not artist_data else query.lastError().text()
                errview = f"'{self.get_all_datas_from_database.__name__}': {errview} (query)" if errview and "kein " not in str(errview) else errview
            del query
        else:       
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_all_datas_from_database.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        artist_data.save_to_json()        
        return errview

    def get_minidatas_from_ordner(self, ordner: str) -> str:
        errview = None 
        artist_data = VideoData()

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT ArtistID, Name, Ordner FROM DB_Artist WHERE Ordner = :Ordner;")
                query.bindValue(":Ordner", ordner)
                query.exec()                
                while query.next():                                        
                    artist_data.initialize(query.record())                    
                errview = f"'{self.get_minidatas_from_ordner.__name__}': {errview} (query1)" if query.lastError().text() else None                 
        else:       
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_minidatas_from_ordner.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        artist_data.save_to_json()        
        return errview
    
    ### --------------------------- Rassen --------------------------- ####
    def get_all_rassen_ger(self) -> list:            
        errview: str=None
        rassen: list=[]     

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT Rasse_ger FROM Rassen;")                                               
                query.exec()       
                while query.next():                    
                    rassen.append(query.value("Rasse_ger"))                
                errview =  f"'{self.get_all_rassen_ger.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_all_rassen_ger.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return rassen 
    
    def get_rassenids_from_artistid(self, artist_id: int) -> list:
        errview: str=None
        rassen_ids: list=[]     

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT RassenID FROM Person_Rasse WHERE ArtistID = :ArtistID;")  
                query.bindValue(":ArtistID", artist_id)                                             
                query.exec()       
                while query.next(): 
                    if query.value("RassenID") > 0:                   
                        rassen_ids.append(query.value("RassenID"))
                errview =  f"'{self.get_rassenids_from_artistid.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None                
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_rassenids_from_artistid.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return rassen_ids 
    
    def get_rassen_id_from_rassen_ger(self, rasse_ger: str) -> int:
        errview: str=None
        rasse_id: int=-1     

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare("SELECT RassenID FROM Rassen WHERE Rasse_ger = :Rasse_ger;")  
                query.bindValue(":Rasse_ger", rasse_ger)                                             
                query.exec()       
                if query.next(): 
                    rasse_id=query.value("RassenID")
                    errview = f"'{self.get_rassen_id_from_rassen_ger.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:                    
                    errview = f"'{self.get_rassen_id_from_rassen_ger.__name__}': kein '{rasse_id}' gefunden in der Datenbank" if rasse_id == -1 else f"'{self.get_rassen_id_from_rassen_ger.__name__}': {query.lastError().text()} (query)"
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_rassen_id_from_rassen_ger.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return rasse_id 
    
    def get_rassen_ger_from_rassen_eng(self, rasse_eng: str) -> str:
        errview: str=None
        rasse_ger: str=""

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT Rasse_ger FROM Rassen WHERE Rasse_eng = :Rasse_eng;")
                query.bindValue(":Rasse_eng", rasse_eng)
                query.exec()
                if query.next():
                    rasse_ger=query.value("Rasse_ger")
                    errview =  f"'{self.get_rassen_ger_from_rassen_eng.__name__}': {query.lastError().text()} (query1)" if query.lastError().text() else None
                else:
                    err_text = query.lastError().text()
                    errview = f"'{self.get_rassen_ger_from_rassen_eng.__name__}': kein '{rasse_ger}' gefunden in der Datenbank" if not err_text else f"'{self.get_rassen_ger_from_rassen_eng.__name__}': {err_text} (query)"
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_rassen_ger_from_rassen_eng.__name__}'" if self.db.lastError().text() else errview                      
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return rasse_ger
    
    ############################################################################################ 
    ###------------------------ Daten in die Datenbank adden ------------------------------- ###
    ############################################################################################
    def add_artistid_from_name_ordner(self, name: str, ordner: str) -> int:
        artist_id: int=-1
        errview: str=None

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("INSERT INTO DB_Artist (Name, Ordner) VALUES (:Name, :Ordner);")
                query.bindValue(":Name", name)
                query.bindValue(":Ordner", ordner)
                if query.exec():
                    artist_id = query.lastInsertId()
                else:
                    errview = f"'{self.add_artistid_from_name_ordner.__name__}': {query.lastError().text()}" if query.lastError().text() else None
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.add_artistid_from_name_ordner.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return artist_id

    def addDarsteller_in_db(self, performer_data: dict, studio: str=None) -> tuple[str, int, int, int, int]:
        errview: str=None
        artist_neu: int=0
        sex_neu: int=0
        link_neu: int=0
        new_artist_id=0

        self.open_database()
        if self.db.isOpen():  
            if studio:        
                with self.managed_query() as query:
                    # Überprüfen, ob das Studio in der Datenbank vorhanden ist
                    query.prepare("SELECT StudioID FROM Studios WHERE StudioName=:StudioName;")
                    query.bindValue(":StudioName", studio)
                    query.exec()
                    if query.next():
                        studio_id = query.value('StudioID')
                        errview = query.lastError().text() if query.lastError().text() else None
                    else:
                        # Wenn das Studio nicht in der DB ist, neu hinzufügen und die ID abrufen
                        with self.managed_query() as query:
                            query.prepare("INSERT INTO Studios (StudioName) VALUES (:StudioName);")
                            query.bindValue(":StudioName", studio)
                            query.exec()
                            errview = query.lastError().text() if query.lastError().text() else errview
                        with self.managed_query() as query:
                            query.prepare("SELECT MAX(StudioID) FROM Studios;")
                            query.exec()
                            query.next()
                            studio_id = query.value('MAX(StudioID)')
                            errview = query.lastError().text() if query.lastError().text() else errview
            else: ### ----------- studio nicht angegeben -------------- ###
                with self.managed_query() as query:
                    query.prepare("SELECT ArtistID FROM DB_Artist WHERE Ordner=:Ordner;")
                    query.bindValue(":Ordner", performer_data["Ordner"])
                    query.exec()
                    errview = query.lastError().text() if query.lastError().text() else errview
                    if query.next():                        
                        artist_id = query.value('ArtistID')
                        errview = query.lastError().text() if query.lastError().text() else errview
                        # Geschlecht und Nation aktualisieren, wenn erforderlich
                        with self.managed_query() as query:
                            query.prepare("UPDATE DB_Artist SET Ordner=:Ordner, Geschlecht=IFNULL(:Geschlecht, Geschlecht), "
                                        "Nation=IFNULL(:Nation, Nation) WHERE ArtistID=:ArtistID;")
                            query.bindValue(":Geschlecht", performer_data["Geschlecht"])
                            query.bindValue(":Ordner", performer_data["Ordner"])
                            query.bindValue(":Nation", performer_data["Nation"])
                            query.bindValue(":ArtistID", artist_id)
                            if query.exec():
                                sex_neu = 1
                            else:
                                errview = query.lastError().text() if query.lastError().text() else errview
                    else:
                        # Wenn der Künstler nicht vorhanden ist, legen Sie ihn neu an
                        with self.managed_query() as query:                            
                            query.prepare("INSERT INTO DB_Artist (ArtistID, Name, Ordner, Geschlecht, Nation) "
                                        "VALUES (NULL, :Name, :Ordner, :Geschlecht, :Nation);")
                            query.bindValue(":Name", performer_data["Name"])
                            query.bindValue(":Ordner", performer_data["Ordner"])
                            query.bindValue(":Geschlecht", performer_data["Geschlecht"])
                            query.bindValue(":Nation", performer_data["Nation"])
                            query.exec()
                            errview = query.lastError().text() if query.lastError().text() else errview
                        # Holen Sie die zugehörige ID ab
                        with self.managed_query() as query:                            
                            query.prepare("SELECT max(ArtistID) FROM DB_Artist;")
                            query.exec()
                            query.next()
                            new_artist_id = query.value('max(ArtistID)')
                            errview = query.lastError().text() if query.lastError().text() else errview
                        artist_neu = 1
                    # Wenn der Künstler neu ist oder Informationen fehlen, fügen Sie NamesLink hinzu
                    if artist_neu == 1 and performer_data["ArtistLink"] is not None:
                        with self.managed_query() as query:                            
                            query.prepare("INSERT INTO DB_NamesLink (NamesID, Link, Image, ArtistID, StudioID) "
                                        "VALUES (NULL, IFNULL(:Link, ''), IFNULL(:Image, ''), :ArtistID, :StudioID);")
                            query.bindValue(":Link", performer_data["ArtistLink"])
                            query.bindValue(":Image", performer_data["ImagePfad"])
                            query.bindValue(":ArtistID", new_artist_id)
                            query.bindValue(":StudioID", studio_id)
                            query.exec()
                            errview = query.lastError().text() if query.lastError().text() else errview
                        link_neu = 1
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.addDarsteller_in_db.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return errview, artist_neu, sex_neu, link_neu, new_artist_id
    
    def add_db_artistlink(self, artist_id: int, names_link_satz: dict, studio_id: int) -> int:
        errview: str=None 
        is_addet: int=0 
        names_id: int=0       

        self.open_database()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("INSERT INTO DB_NamesLink (NamesID, Link, Image, ArtistID, StudioID, Alias) VALUES (NULL, :Link, :Image, :ArtistID, :StudioID, :Alias);")   
                query.bindValue(":Link",names_link_satz["Link"])
                query.bindValue(":Image",names_link_satz["Image"])
                query.bindValue(":ArtistID",artist_id)
                query.bindValue(":StudioID",studio_id)
                query.bindValue(":Alias",names_link_satz["Alias"])
                if query.exec():
                    names_id = query.lastInsertId()
                    is_addet=1 
                errview = query.lastError().text() if query.lastError().text() else None  
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.add_db_artistlink.__name__}'" if self.db.lastError().text() else errview 
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return is_addet, names_id

    def addMovie(self,PornSide,VideoTitel,VideoLink,Dauer,Resize,Bitrate,Ursprung,ArtistID,Tags,Beschreibung,ReleaseDate,DownloadDate,DateiGroesse,Regie,MovieTitel,FilmLink,HDDLink):
        errview: str=None 
        artist_ids: list=[]
        neu: int=0

        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager
            with self.managed_query() as query:
                query.prepare("SELECT MovieID FROM DB_Movies WHERE VideoTitel=:VideoTitel AND HDDLink=:HDDLink;")
                query.bindValue(":VideoTitel",VideoTitel)
                query.bindValue(":HDDLink",HDDLink)
                if query.next():
                    movie_id=query.value("MovieID")
                    errview = query.lastError().text() if query.lastError().text() else errview
                else:
                    with self.managed_query() as query:
                        query.prepare("INSERT INTO DB_Movies (MovieID,StudioID,VideoTitel,VideoLink,Dauer,Resize,Bitrate,\
                            Ursprung,ArtistID,Tags,Beschreibung,ReleaseDate,DownloadDate,DateiGroesse,Regie,MovieTitel,FilmLink,\
                            HDDLink) VALUES (NULL,{movie_id},'{VideoTitel}','{VideoLink}','{Dauer}','{Resize}',{Bitrate},\
                            '{Ursprung}','{ArtistID}','{Tags}','{Beschreibung}','{ReleaseDate}','{DownloadDate}',{DateiGroesse},\
                            '{Regie}','{MovieTitel}','{FilmLink}','{HDDLink}');")
                        query.bindValue(":StudioID",movie_id)
                        query.bindValue(":VideoTitel",VideoTitel)
                        query.bindValue(":VideoLink",VideoLink)
                        query.bindValue(":Dauer",Dauer)
                        query.bindValue(":Resize",Resize)
                        query.bindValue(":Bitrate",Bitrate)
                        query.bindValue(":Ursprung",Ursprung)                        
                        query.bindValue(":ArtistID",ArtistID)
                        query.bindValue(":Tags",Tags)#
                        query.bindValue(":Beschreibung",Beschreibung)
                        query.bindValue(":ReleaseDate",ReleaseDate)
                        query.bindValue(":DownloadDate",DownloadDate)
                        query.bindValue(":DateiGroesse",DateiGroesse)
                        query.bindValue(":Regie",Regie)
                        query.bindValue(":MovieTitel",MovieTitel)
                        query.bindValue(":FilmLink",FilmLink)
                        query.bindValue(":HDDLink",HDDLink)                        
                        query.exec() 
                        errview = query.lastError().text() if query.lastError().text() else errview
                    errview = query.lastError().text() if query.lastError().text() else errview    
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.addMovie.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()      
    
    def webside_infos(self,studio: str, homepage: str) -> Tuple[int, int]:
        errview: str=None        
        neu: int=0
        add: int=0
        studio_id: str=None

        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager        
            with self.managed_query() as query:
                query.prepare("SELECT StudioID, StudioName, Homepage FROM Studios WHERE StudioName = :StudioName OR \
                            Homepage = :Homepage")
                query.bindValue(":StudioName", studio)
                query.bindValue(":Homepage", homepage)
                query.exec()        
                if query.next():            
                    studio_id=query.value("StudioID")
                    neu,studio=(1, self.query.value("StudioName")) if studio == ("" or self.query.value("StudioName")) else (0, studio)
                    neu,homepage=(1, self.query.value("Homepage")) if homepage == ("" or self.query.value("Homepage")) else (0, homepage)                
                if neu==1:   ### -------- Wenn kein Link da ist, dann Update --------- ### 
                    with self.managed_query() as query:
                        query.prepare("UPDATE Studios SET StudioName = :StudioName, Homepage = :Homepage WHERE StudioID = :StudioID")
                        query.bindValue(":StudioName", studio)
                        query.bindValue(":Homepage", homepage) 
                        query.bindValue(":StudioID", studio_id)                
                        query.exec()                
                else:
                    if studio_id==None:
                        with self.managed_query() as query:
                            query.prepare("INSERT INTO Studios (StudioID, StudioName, Homepage) VALUES (NULL,:StudioName,:Homepage)")
                            query.bindValue(":StudioName", studio)
                            query.bindValue(":Homepage", homepage)   
                            query.exec()
                            add=1
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.webside_infos.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()         
        return neu, add 

    def add_performer_link_and_image(self, iafd_datensatz: dict) -> Tuple[str, bool]:            
        errview: str=None        
        is_addet: bool=False
        ### --------- database ----------- ###
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query: 
                query.prepare("INSERT INTO DB_NamesLink (NamesID, Link, Image, ArtistID, StudioID, Alias) VALUES (NULL, :Link, :Image, :ArtistID, 69, :Alias)")
                query.bindValue(":Link",iafd_datensatz["Link"]) 
                query.bindValue(":Image",iafd_datensatz["Image"])
                query.bindValue(":ArtistID",iafd_datensatz["ArtistID"])
                query.bindValue(":Alias",iafd_datensatz["Alias"]) 
                if query.exec(): 
                    if query.numRowsAffected() > 0:                   
                        is_addet = True
                else:
                    errview = f"'{self.add_performer_link_and_image.__name__}': {query.lastError().text()}" if query.lastError().text() else None                                
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.add_performer_link_and_image.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, is_addet
    
    ############################################################################################ 
    ###------------------------ Daten in der Datenbank updaten ----------------------------- ###
    ############################################################################################
    def set_black_people(self,studio,geschlecht):
        errview: str=None
        artist_ids: list=[]
        neu: int=0
        
        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager
            with self.managed_query() as query:
                query.prepare("SELECT StudioID FROM Studios WHERE StudioName= :StudioName;")
                query.bindValue(":StudioName",studio)
                query.exec()
                if self.query.next():
                    studio_id=query.value("StudioID")
                    errview = query.lastError().text() if query.lastError().text() else errview
            with self.managed_query() as query:
                query.prepare("SELECT DB_Artist.ArtistID,RassenID FROM DB_Artist INNER JOIN DB_NamesLink ON DB_Artist.ArtistID \
                    = DB_NamesLink.ArtistID INNER JOIN Studios ON Studios.StudioID = DB_NamesLink.StudioID \
                    WHERE Studios.StudioID=:StudioID And Geschlecht=:Geschlecht;")
                query.bindValue(":StudioID",studio_id)
                query.bindValue(":Geschlecht",geschlecht)
                query.exec()        
                while query.next():                
                    artist_id=query.value("DB_Artist.ArtistID")
                    rassen_id=query.value("RassenID")
                    errview = query.lastError().text() if query.lastError().text() else errview
                    if rassen_id=="":
                        artist_ids.append(artist_id)
                for artist_id in artist_ids:
                    with self.managed_query() as query:
                        query.prepare("UPDATE DB_Artist SET RassenID=:RassenID WHERE ArtistID=:ArtistID;")
                        query.bindValue(":RassenID",3)
                        query.bindValue(":ArtistID",artist_id)
                        query.exec()
                        neu+=1 
                errview = query.lastError().text() if query.lastError().text() else errview 
        else:   
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.set_black_people.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return neu
    
    def update_performer_datensatz(self, performer_data: dict) -> Tuple[str, bool]:
        errview: str=None        
        is_update: bool=False

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:                 
                placeholders = ', '.join([f"{field}=:{field}" for field in performer_data.keys() if field != "ArtistID"])
                sql_query = f'UPDATE DB_Artist SET {placeholders} WHERE ArtistID= :ArtistID;'
                query.prepare(sql_query)
                query.bindValue(":ArtistID",performer_data["ArtistID"])
                for field, value in performer_data.items():
                    if field != "ArtistID":
                        query.bindValue(f":{field}", value)
                if query.exec(): 
                    if query.numRowsAffected() > 0:                   
                        is_update = True
                    errview = query.lastError().text() if query.lastError().text() else errview                                
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.update_performer_datensatz.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, is_update  
    
    def update_artistid_from_names_id(self, names_id: int, artist_id) -> Tuple[str, int]:
        errview: str=None        
        is_update: int=0
        # ------ database ------- #
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query: 
                query.prepare('UPDATE DB_NamesLink SET ArtistID=:ArtistID WHERE NamesID= :NamesID;')
                query.bindValue(":NamesID",names_id)
                query.bindValue(":ArtistID",artist_id)                
                if query.exec(): 
                    is_update = query.numRowsAffected()
                else:
                    errview = f"{self.update_artistid_from_names_id.__name__}: {query.lastError().text()}" if query.lastError().text() else None                               
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.update_artistid_from_names_id.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, is_update 

    def update_performer_names_link(self, artist_id: int,links: list, studio_id: int) -> Tuple[str, int]:
        errview: str=None        
        is_update: int=0
        # ------ database ------- #
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:                
                placeholders = ', '.join([f"{field}=:{field}" for field in links.keys()])                    
                query.prepare(f'UPDATE DB_NamesLink SET {placeholders}, ArtistID=:ArtistID, StudioID=:StudioID WHERE NamesID= :NamesID;')                    
                query.bindValue(":ArtistID", artist_id)
                query.bindValue(":StudioID", studio_id)
                for field, value in links.items():
                    query.bindValue(f":{field}", value)
                if query.exec(): 
                    is_update = query.numRowsAffected()
                    errview = query.lastError().text() if query.lastError().text() else errview                                
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.update_performer_datensatz.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return is_update 
    
    ############################################################################################
    ###------------------------ Daten aus der Datenbank adden and updaten zusammen --------- ###
    ############################################################################################
    ###------------------------ Update/Add -- Rassen --------------------------------------- ###
    def update_or_add_rassen_datensatz(self, rassen_ids: list, artist_id: int) -> Tuple[str, bool]:
        errview: str = None
        update_or_add: int = 0 
        is_update: bool=False       
        # ------ Datenbankverbindung öffnen ------- #
        self.open_database()
        if self.db.isOpen(): 
            # Bestehende Rassen-IDs abrufen
            errview, existing_personids_rassenids = self.get_existing_rassen_ids(artist_id, errview)
            # Löschen von nicht mehr zutreffenden Einträgen
            for existing_person_id, existing_rassen_id in existing_personids_rassenids:
                if existing_rassen_id not in rassen_ids:
                    errview, delete = self.delete_rassen_datensatz(existing_rassen_id, artist_id, errview)
                    update_or_add += delete
                # Hinzufügen von fehlenden Einträgen
            for rassen_id in rassen_ids:
                existing_person_id = next((person_id for person_id, existing_rassen_id in existing_personids_rassenids if existing_rassen_id == rassen_id), None)
                if existing_person_id is None:
                    # PersonID nicht gefunden, also hinzufügen
                    errview, added = self.add_rassen_datensatz(rassen_id, artist_id, errview)
                    update_or_add += added
                else:
                    # PersonID gefunden, also aktualisieren
                    errview, update = self.update_rasseid_datensatz(existing_person_id, rassen_id, artist_id, errview)
                    update_or_add += update
            # Überprüfen, ob Änderungen vorgenommen wurden
            is_update = update_or_add == (len(rassen_ids) or len(existing_personids_rassenids))                
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.update_or_add_rassen_datensatz.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, is_update
    
    def get_existing_rassen_ids(self, artist_id: int, errview: str) -> list:
        existing_person_rassen_ids: list = []
        with self.managed_query() as query:
            query.prepare("SELECT PersonID, RassenID FROM Person_Rasse WHERE ArtistID=:ArtistID;")
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            if query.lastError().isValid():
                # Ein Fehler ist aufgetreten
                errview = query.lastError().text()
            else:
                while query.next():
                    existing_person_rassen_ids.append((query.value(0), query.value(1)))            
        del query
        return errview, existing_person_rassen_ids
    
    def delete_rassen_datensatz(self, rassen_id: int, artist_id: int, errview: str) -> int:
        del_dataset: int = 0
        with self.managed_query() as query:
            query.prepare("DELETE FROM Person_Rasse WHERE RassenID=:RassenID AND ArtistID=:ArtistID;")
            query.bindValue(":RassenID", rassen_id)
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            errview = query.lastError().text() if query.lastError().text() else errview
            del_dataset = query.numRowsAffected()
        del query
        return errview, del_dataset
    
    def add_rassen_datensatz(self, rassen_id: int, artist_id: int, errview: str) -> int:
        del_dataset: int = 0
        with self.managed_query() as query:
            query.prepare("INSERT INTO Person_Rasse (PersonID, RassenID, ArtistID) VALUES (NULL, :RassenID, :ArtistID);")
            query.bindValue(":RassenID", rassen_id)
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            errview = query.lastError().text() if query.lastError().text() else errview
            add_dataset = query.numRowsAffected()
        del query
        return errview, add_dataset
    
    def update_rasseid_datensatz(self, person_id: int, rassen_id: int, artist_id: int, errview: str) -> int:
        update_dataset: int = 0
        with self.managed_query() as query:
            query.prepare("UPDATE Person_Rasse SET RassenID=:RassenID WHERE PersonID=:PersonID AND ArtistID=:ArtistID;")
            query.bindValue(":PersonID", person_id)
            query.bindValue(":RassenID", rassen_id)
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            errview = query.lastError().text() if query.lastError().text() else errview
            update_dataset = query.numRowsAffected()
        del query
        return errview, update_dataset
    ### ---------------------------------------------------------------------------------- ###
    ###------------------------ Update/Add -- Nationen ----------------------------------- ###
    def update_or_add_nation_datensatz(self, nation_ids: list, artist_id: int) -> Tuple[str, bool]:
        errview: str = None
        update_or_add: int = 0 
        is_update: bool=False       
        # ------ Datenbankverbindung öffnen ------- #
        self.open_database()
        if self.db.isOpen(): 
            # Bestehende Nation-IDs abrufen
            errview, existing_personids_nationids = self.get_existing_nation_ids(artist_id, errview)
            # Löschen von nicht mehr zutreffenden Einträgen
            for existing_person_id, existing_nation_id in existing_personids_nationids:
                if existing_nation_id not in nation_ids:
                    errview, delete = self.delete_nation_datensatz(existing_nation_id, artist_id, errview)
                    update_or_add += delete
                # Hinzufügen von fehlenden Einträgen
            for nation_id in nation_ids:
                existing_person_id = next((person_id for person_id, existing_nation_id in existing_personids_nationids if existing_nation_id == nation_id), None)
                if existing_person_id is None:
                    # PersonID nicht gefunden, also hinzufügen
                    errview, added = self.add_nation_datensatz(nation_id, artist_id, errview)
                    update_or_add += added
                else:
                    # PersonID gefunden, also aktualisieren
                    errview, update = self.update_nationid_datensatz(existing_person_id, nation_id, artist_id, errview)
                    update_or_add += update
            # Überprüfen, ob Änderungen vorgenommen wurden
            is_update = update_or_add == (len(nation_ids) or len(existing_personids_nationids))                
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.update_or_add_nation_datensatz.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, is_update
    
    def get_existing_nation_ids(self, artist_id: int, errview: str) -> list:
        existing_person_nation_ids: list = []
        with self.managed_query() as query:
            query.prepare("SELECT PersonID, NationID FROM Person_Nation WHERE ArtistID=:ArtistID;")
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            if query.lastError().isValid():
                # Ein Fehler ist aufgetreten
                errview = query.lastError().text()
            else:
                while query.next():
                    existing_person_nation_ids.append((query.value(0), query.value(1)))            
        del query
        return errview, existing_person_nation_ids
    
    def delete_nation_datensatz(self, nation_id: int, artist_id: int, errview: str) -> int:
        del_dataset: int = 0
        with self.managed_query() as query:
            query.prepare("DELETE FROM Person_Nation WHERE NationID=:NationID AND ArtistID=:ArtistID;")
            query.bindValue(":NationID", nation_id)
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            errview = query.lastError().text() if query.lastError().text() else errview
            del_dataset = query.numRowsAffected()
        del query
        return errview, del_dataset
    
    def add_nation_datensatz(self, nation_id: int, artist_id: int, errview: str) -> int:
        del_dataset: int = 0
        with self.managed_query() as query:
            query.prepare("INSERT INTO Person_Nation (PersonID, NationID, ArtistID) VALUES (NULL, :NationID, :ArtistID);")
            query.bindValue(":NationID", nation_id)
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            errview = query.lastError().text() if query.lastError().text() else errview
            add_dataset = query.numRowsAffected()
        del query
        return errview, add_dataset
    
    def update_nationid_datensatz(self, person_id: int, nation_id: int, artist_id: int, errview: str) -> int:
        update_dataset: int = 0
        with self.managed_query() as query:
            query.prepare("UPDATE Person_Nation SET NationID=:NationID WHERE PersonID=:PersonID AND ArtistID=:ArtistID;")
            query.bindValue(":PersonID", person_id)
            query.bindValue(":NationID", nation_id)
            query.bindValue(":ArtistID", artist_id)
            query.exec()
            errview = query.lastError().text() if query.lastError().text() else errview
            update_dataset = query.numRowsAffected()
        del query
        return errview, update_dataset
    ### ---------------------------------------------------------------------------------- ###
    
    
    ############################################################################################ 
    ###------------------------ Daten aus der Datenbank löschen/deleten -------------------- ###
    ############################################################################################    
    def delete_nameslink_satz(self, names_id: int) -> bool:           
        errview: str=None        
        is_delete: int=False

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:  
                query.prepare('DELETE FROM DB_NamesLink WHERE NamesID = :NamesID;')                    
                query.bindValue(":NamesID", names_id)
                if query.exec(): 
                    is_delete = True                    
                else:
                    errview = f"'{self.delete_nameslink_satz.__name__}': {query.lastError().text()} (query)" if query.lastError().text()  else None
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.delete_nameslink_satz.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return is_delete
    
    def delete_performer_dataset(self, artist_id: int) -> bool:           
        errview: str=None        
        is_delete: int=False

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:  
                query.prepare('DELETE FROM DB_Artist WHERE ArtistID = :ArtistID;')                    
                query.bindValue(":ArtistID", artist_id)
                if query.exec(): 
                    is_delete = True                    
                else:
                    errview = f"'{self.delete_performer_dataset.__name__}': {query.lastError().text()} (query)" if query.lastError().text()  else None
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.delete_performer_dataset.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return is_delete

    ############################################################################################ 
    ###------------------------ Daten in der Datenbank holen ------------------------------- ###
    ############################################################################################
    def hole_db_artistlink(self, artistname: str, studio: str) -> str:
        errview: str=None 
        link: str=None

        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager        
            with self.managed_query() as query:
                query.prepare("SELECT Geschlecht,DB_NamesLink.Link FROM DB_Artist INNER JOIN DB_NamesLink ON \
                    DB_Artist.ArtistID = DB_NamesLink.ArtistID INNER JOIN Studios ON Studios.StudioID \
                    = DB_NamesLink.StudioID WHERE Name = :Name and StudioName = :StudioName;")
                query.bindValue(":Name",artistname)
                query.bindValue(":StudioName",studio) 
                query.exec()        
                if query.next():                
                    link=query.value("DB_NamesLink.Link")
                    errview = f"'{self.hole_db_artistlink.__name__}': {query.lastError().text()} (query1)" if query.lastError().text()  else None
                else:
                    errview = f"keine Links für {artistname} gefunden" if not query.lastError().text() else f"'{self.hole_db_artistlink.__name__}': {query.lastError().text()} (query)"    
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_db_artistlink.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()         
        return link

    def suche_nach_artistname(self,artistname: str) -> str:
        errview: str= None 
        name: list=[] 

        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager               
            with self.managed_query() as query:
                query.prepare("SELECT Name FROM DB_Artist WHERE Name Like :Name_ OR Name=:Name;")
                query.bindValue(":Name_",f'{artistname} %')
                query.bindValue(":Name",artistname)
                query.exec()                
                while query.next():
                    name.append(query.value('Name'))
                    errview = query.lastError().text() if query.lastError().text() else errview
                errview = (errview or f"keine Links für {artistname} gefunden") if not query.lastError().text() and not name else query.lastError().text()    
                errview = f"{errview} (query)" if errview and "keine " not in str(errview) else errview
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_performers_picture.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()                 
        return name
    
    def get_performers_picture(self, performer_name: str) -> Tuple[str, list, list]:
        errview: str= None 
        images: list=[]
        links: list=[]

        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager            
            with self.managed_query() as query:                 
                query.prepare('SELECT DB_NamesLink.Image, DB_NamesLink.Link FROM DB_Artist JOIN DB_NamesLink ON DB_Artist.ArtistID = DB_NamesLink.ArtistID WHERE DB_Artist.Name = :Name;')
                query.bindValue(":Name",performer_name)                
                query.exec()                           
                while query.next():
                    images.append(query.value("DB_NamesLink.Image"))
                    links.append(query.value("DB_NamesLink.Link"))
                    errview = query.lastError().text() if query.lastError().text() else errview
                errview = (errview or f"keine Links für {performer_name} gefunden") if not query.lastError().text() and not links else query.lastError().text()
                errview = f"'{self.get_performers_picture.__name__}': {errview} (query)" if errview and "keine " not in str(errview) else errview
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_performers_picture.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()                
        return errview, images, links 

    def get_quell_links(self, artist_id: int) -> list:
        errview = None
        ids: list=[]
        links: list=[]
        images: list=[]
        aliases: list=[]        
        
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT NamesID, Link, Image, Alias FROM DB_NamesLink WHERE ArtistID = :ArtistID;")
                query.bindValue(":ArtistID", artist_id)                
                query.exec()                
                while query.next(): 
                    ids.append(query.value("NamesID"))                   
                    links.append(query.value("Link"))
                    images.append(query.value("Image")) 
                    aliases.append(query.value("Alias"))
                    errview = f"'{self.get_quell_links.__name__}': {errview} (query1)" if query.lastError().text() else errview
                errview = (errview or f"kein ID:{artist_id} gefunden in Links") if not query.lastError().text() and not ids else query.lastError().text()
                errview = f"'{self.get_quell_links.__name__}': {errview} (query)" if errview and "kein " not in str(errview) else errview
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_quell_links.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()               
        return [ids, links, images, aliases]
    
    def get_performer_dataset_from_artistid(self, artist_id: int) -> dict:
        errview: str = None 
        artist_data = VideoData()

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT * FROM DB_Artist WHERE ArtistID = :ArtistID;")
                query.bindValue(":ArtistID", artist_id)                
                query.exec()                
                if query.next():                                        
                    artist_data.initialize(query.record())
                else:
                    errview = f"'{self.get_performer_dataset_from_artistid.__name__}': {errview} (query)" if query.lastError().text() else None
        else:       
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_performer_dataset_from_artistid.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()             
        return artist_data.get_data() 

    
    def get_iafd_image(self, artist_id: int=0, name=None) -> Tuple[str, str]:            
        errview = None
        image_pfad: str=None  
        images: str=None      
        
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT DB_NamesLink.ArtistID, DB_NamesLink.Image FROM DB_Artist LEFT JOIN DB_NamesLink ON DB_NamesLink.ArtistID = DB_Artist.ArtistID WHERE DB_NamesLink.ArtistID = :ArtistID AND (DB_Artist.Name = :Name OR :Name IS NULL);")
                query.bindValue(":ArtistID", artist_id) 
                query.bindValue(":Name", name)               
                query.exec()                
                while query.next(): 
                    images=query.value("DB_NamesLink.Image")                     
                    if "[IAFD]" in images:
                        image_pfad=images 
                        break  
                    errview = f"'{self.get_iafd_image.__name__}': {errview} (query1)" if query.lastError().text() else errview
                errview = (errview or f"keine ID:{artist_id} für IAFD Image gefunden in 'Links'") if not query.lastError().text() and not image_pfad else query.lastError().text()
                errview = f"'{self.get_iafd_image.__name__}': {errview} (query)" if errview and "keine " not in str(errview) else errview
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_iafd_image.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()               
        return errview, image_pfad
    
    def get_babepedia_image(self, artist_id: int=0, name=None) -> Tuple[str, str]:            
        errview = None
        image_pfad: str=None  
        images: str=None      
        
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT DB_NamesLink.ArtistID, DB_NamesLink.Image FROM DB_Artist LEFT JOIN DB_NamesLink ON DB_NamesLink.ArtistID = DB_Artist.ArtistID WHERE DB_NamesLink.ArtistID = :ArtistID OR DB_Artist.Name = :Name;")
                query.bindValue(":ArtistID", artist_id) 
                query.bindValue(":Name", name)               
                query.exec()                
                while query.next(): 
                    images=query.value("DB_NamesLink.Image")                     
                    if "[BabePedia]" in images:
                        image_pfad=images 
                        break  
                    errview = f"'{self.get_babepedia_image.__name__}': {errview} (query1)" if query.lastError().text() else None
                #errview = (errview or f"keine ID:{artist_id} für BabePedia Image gefunden in 'Links'") if not query.lastError().text() and not image_pfad else query.lastError().text()
                errview = f"'{self.get_babepedia_image.__name__}': {errview} (query)" if errview else errview #and "keine " not in str(errview)
            del query
        else:
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_babepedia_image.__name__}'" if self.db.lastError().text() else errview          
        if errview:
            self.db_fehler(errview)
        self.close_database()               
        return errview, image_pfad

if __name__ == "__main__":
    DB_Darsteller()