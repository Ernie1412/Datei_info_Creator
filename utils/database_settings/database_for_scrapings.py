from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlField
from PyQt6.QtCore import QDateTime
from contextlib import contextmanager
import json
from typing import List, Tuple

from config import SIDE_DATAS_DB_PATH, DB_RECORD_JSON

class VideoData():   

    def __init__(self):
        self.data = []

    def __len__(self):
        return len(self.data)
    
    def get_data(self):
        return self.data
    
    def save_data(self, data):
        self.data=data
    
    def initialize(self, record=None):
        data_satz={}  
        if record:            
            for i in range(record.count()):
                field = record.field(i)
                data_satz[field.name()] = field.value() 
            self.data.append(data_satz)          

    def load_from_json(self):
        # Lade die Daten aus einer JSON-Datei in das Objekt
        try:
            with open(DB_RECORD_JSON, 'r') as json_file:
                self.data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []
        return self.data

    def save_to_json(self):
        # Speichere die Daten aus dem Objekt in einer JSON-Datei
        with open(DB_RECORD_JSON, 'w') as json_file:
            json.dump(self.data, json_file, indent=4, sort_keys=True)


class ScrapingData:
   
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

    def open_database(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE",'db_movie_data')
        self.db.setHostName("localhost")        
        self.db.setDatabaseName(SIDE_DATAS_DB_PATH)
        self.db.open()           

    def close_database(self):
        self.db.close()            
        connection_name = self.db.connectionName()
        del self.db 
        QSqlDatabase.database(connection_name).close()  
        QSqlDatabase.removeDatabase(connection_name)# Vorhandene Verbindung schließen        

    def db_fehler(self,fehler: str) -> None:
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        if fehler.startswith("kein"):
            self.Main.lbl_db_status.setStyleSheet("background-color : #FFCB8F")
        else:
            self.Main.lbl_db_status.setStyleSheet("background-color : #FA5882")
        self.Main.lbl_db_status.setText(f"{current_time} --> {fehler}")  
    
    ###########################################################################
    #### ------------ hole Daten aus der Datenbank ----------------------- ####
    ###########################################################################  
        
    def get_id_from_websidelink(self, link: str, studio: str) -> str:
        errview = None        
        id = None

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT ID FROM '{studio}' WHERE WebsideLink = :webside;")
                query.bindValue(":webside", f"{link}")
                query.exec()                
                if query.next(): 
                    id = query.value("ID")
                errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_id_from_websidelink.__name__}'" if self.db.lastError().text() else None        
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, id

    def hole_videodatas_von_performer(self, performers: str, studio: str) -> str:
        errview = None
        video_data = VideoData()
        
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT ID, Titel, WebSideLink, IAFDLink, Performers, Alias, Action, ReleaseDate, ProductionDate, Serie, Regie, SceneCode, Dauer, Movies, Synopsis, Tags FROM '{studio}' WHERE Performers LIKE :Performers;")
                query.bindValue(":Performers", f"%{performers}%")
                query.exec()                
                while query.next():                    
                    video_data.initialize(query.record()) 
                    errview = f"'{self.hole_videodatas_von_performer.__name__}': {errview} (query1)" if query.lastError().text() else errview
                errview = (errview or f"kein {performers} gefunden in {studio}") if not query.lastError().text() and not video_data else query.lastError().text()
                errview = f"'{self.hole_videodatas_von_performer.__name__}': {errview} (query)" if errview and "kein " not in str(errview) else errview
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_videodatas_von_performer.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        video_data.save_to_json()        
        return errview


    def hole_link_aus_db(self, link: str, studio: str) -> str:
        errview = None  
        video_data = VideoData()      

        self.open_database()
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare(f"SELECT * FROM '{studio}' WHERE INSTR(LOWER(WebSideLink), LOWER(:Link)) = 1;")
                query.bindValue(":Link", link)
                query.exec()
                while query.next():                    
                    video_data.initialize(query.record())
                    errview = f"'{self.hole_link_aus_db.__name__}': {errview} (query1)" if query.lastError().text() else errview
                errview = (errview or f"kein {link} gefunden in {studio}") if not query.lastError().text() and not video_data else query.lastError().text()
                errview = f"'{self.hole_link_aus_db.__name__}': {errview} (query)" if errview and "kein " not in str(errview) else errview
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_link_aus_db.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()

        video_data.save_to_json()
        return errview
    
    def hole_data18link_von_db(self, id: str, studio: str) -> str:        
        errview = None
        data18_link: str = None
        
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT Data18Link FROM '{studio}' WHERE ID=:ID;")
                query.bindValue(":ID",id)
                query.exec()
                if query.next():
                    data18_link = query.value("Data18Link")                    
                else:
                    errview = f"'{self.hole_data18link_von_db.__name__}': {errview} (query)" if bool(self.db.lastError().text()) else (errview or f"kein Data18 Link gefunden bei '{id}'")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_data18link_von_db.__name__}'" if bool(self.db.lastError().text()) else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return data18_link
    
    def hole_theporndblink_von_db(self, id: str, studio: str) -> str:        
        errview = None
        theporndb_link: str = None
        
        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT ThePornDB FROM '{studio}' WHERE ID=:ID;")
                query.bindValue(":ID",id)
                query.exec()
                if query.next():
                    theporndb_link = query.value("ThePornDB")                    
                else:
                    errview = f"'{self.hole_theporndblink_von_db.__name__}': {errview} (query)" if bool(self.db.lastError().text()) else (errview or f"kein ThePornDB Link gefunden bei '{id}'")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_theporndblink_von_db.__name__}'" if bool(self.db.lastError().text()) else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return theporndb_link
    
    def hole_dauer_von_db(self, webside_link: str, studio: str) -> str: 
        errview = None       
        dauer: str=None

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT Dauer FROM '{studio}' WHERE INSTR(LOWER(WebSideLink), LOWER(:Link)) = 1")
                query.bindValue(":Link",webside_link)
                query.exec()
                if query.next():
                    dauer=query.value("Dauer")
                    errview = f"kein Runtime gefunden in {webside_link}" if not query.lastError().text() and not dauer else query.lastError().text()
                else:
                    errview = f"'{self.hole_dauer_von_db.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"kein Runtime gefunden in {webside_link}")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_dauer_von_db.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return dauer
        
    def hole_titel_aus_db(self, titel: str,studio: str) -> str:           
        errview: str = None 
        video_data = VideoData()       
               
        self.open_database()
        if self.db.isOpen():            
            with self.managed_query() as query:
                if titel == "*":
                    titel = ""
                query.prepare(f"SELECT * FROM '{studio}' WHERE Titel LIKE :titel")                
                query.bindValue(":titel", f"%{titel}%")
                query.exec()                 
                while query.next():
                    video_data.initialize(query.record())
                    errview = f"'{self.hole_titel_aus_db.__name__}': {errview} (query1)" if query.lastError().text() else errview
                errview = (errview or f"kein {titel} gefunden in {studio}") if not query.lastError().text() and not video_data else query.lastError().text()
                errview = f"'{self.hole_titel_aus_db.__name__}': {errview} (query)" if errview and "kein " not in str(errview) else errview
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_titel_aus_db.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        video_data.save_to_json()
        return errview 

    def hole_webside_movies(self,link: str,studio: str) -> Tuple[str, list]:
        errview: str=None
        movies: list=[] 

        self.open_database()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT Movies FROM '{studio}' WHERE INSTR(LOWER(WebSideLink), LOWER(:Link)) = 1;")
                query.bindValue(":Link", link)
                query.exec()
                if query.next():
                    movies = query.value("Movies").split("\n") if query.value("Movies") else None # Eintrag Movies da, dann in eine Liste                                 
                    errview = f"kein Movie mit dem {link} gefunden in {studio}" if not query.lastError().text() and not movies else query.lastError().text()
                else:
                    errview = f"'{self.hole_webside_movies.__name__}': {errview} (query)" if query.lastError().text() else (errview or f"kein Movie mit dem {link} gefunden in {studio}")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_webside_movies.__name__}'" if self.db.lastError().text() else errview      
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return errview, movies 
    

    def from_link_to_studio(self, link: str) -> str:
        errview: str=None
        studio: str=None
        
        self.open_database()
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare("SELECT Studio FROM AliasTable WHERE LOWER(:WebSideLink) LIKE '%' || LOWER(Links) || '%';")
                query.bindValue(":WebSideLink",f"%{link}%")                
                query.exec()                                                          
                if query.next():                    
                    studio = query.value("Studio")
                    errview = f"'{self.from_link_to_studio.__name__}': {errview} (query1)" if query.lastError().text() else errview
                else:                    
                    errview = f"'{self.from_link_to_studio.__name__}': {errview} (query)" if query.lastError().text() else (errview or "kein {link} für Studio gefunden ! (query)")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim der Funktion:'{self.from_link_to_studio.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()         
        return studio 
    
    ###########################################################################
    #### ------------------------ neue Daten adden ----------------------- ####
    ###########################################################################
    def add_neue_videodaten_in_db(self, studio, webside_link, daten_satz: list) -> Tuple[str, str, int]:             
        errview: str = None
        
        isneu: int = 0
        fields = {
            "Titel": daten_satz["Titel"],
            "WebSideLink": webside_link,
            "Data18Link": daten_satz["Data18Link"],
            "ThePornDB": daten_satz["ThePornDBLink"],
            "IAFDLink": daten_satz["IAFDLink"],
            "ReleaseDate": daten_satz["ReleaseDate"],
            "Dauer": daten_satz["Dauer"],
            "Performers": daten_satz["Performers"],
            "Alias": daten_satz["Alias"],
            "Action": daten_satz["Action"],
            "Synopsis": daten_satz["Synopsis"],
            "Tags": daten_satz["Tags"],
            "Serie": daten_satz["Serie"],
            "SceneCode": daten_satz["SceneCode"],
            "Regie": daten_satz["Regie"],
            "ProductionDate": daten_satz["ProDate"],            
            "Movies": daten_satz["Movies"]
                }
        try:
            self.open_database()

            if self.db.isOpen():
                with self.managed_query() as query:
                    placeholders = ', '.join([f":{field}" for field in fields.keys()])
                    sql_query = f"INSERT INTO '{studio}' (ID, {', '.join(fields.keys())}) VALUES (NULL, {placeholders})"
                    query.prepare(sql_query)
                    for field, value in fields.items():
                        query.bindValue(f":{field}", value)
                    if query.exec():                        
                        isneu = 1
                    else:
                        errview = f"{self.add_neue_videodaten_in_db.__name__}: {query.lastError().text()} (query)"
                del query
        except Exception as e:
            errview = f"Fehler: {str(e)} (db) beim Öffnen von Funktion:'{self.add_neue_videodaten_in_db.__name__}'"            
        finally:
            self.close_database() 
        print(f"{isneu}: {daten_satz['Titel']}")       
        return errview , isneu
    
    ###########################################################################
    #### -------------- Überprüfung ob es in der Datenbank ist ----------- ####
    ###########################################################################
    def is_link_in_db(self, webside_link: str=None, iafdlink: str=None) -> bool:
        errview: str=None
        is_vorhanden: bool=False  

        self.open_database()
        if self.db.isOpen():
            tables=self.db.tables()                     
            for table in tables: 
                if table in ['sqlite_sequence', 'Movies', 'Studios', 'Videos', 'AliasTable']: # Ignore List
                    continue         
                with self.managed_query() as query: 
                    query.prepare(f"SELECT ID FROM '{table}' WHERE WebSideLink LIKE ? OR IAFDLink=?")
                    query.bindValue(0, f"{webside_link}%")
                    query.bindValue(1, iafdlink)                
                    query.exec()        
                    if query.next():
                        errview = f"'{self.is_link_in_db.__name__}': {errview} (query1)" if query.lastError().text() else None
                        is_vorhanden = True
                    errview = f"'{self.is_link_in_db.__name__}': {query.lastError().text()} (query)" if query.lastError().text() else errview 
            errview = f"Fehler: {self.db.lastError().text()} (db) beim der Funktion:'{self.is_link_in_db.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()               
        return is_vorhanden

    def is_studio_in_db(self, studio: str) -> bool:        
        errview: str=None
        is_vorhanden: bool = False

        self.open_database()
        if self.db.isOpen():
            tables=self.db.tables()        
            if studio in tables:
                is_vorhanden = True 
            errview = f"Fehler: {self.db.lastError().text()} (db) beim der Funktion:'{self.is_studio_in_db.__name__}'" if self.db.lastError().text() else errview
        if errview:
            self.db_fehler(errview)
        self.close_database()               
        return is_vorhanden   
    ###########################################################################
    #### ------------------------ update Daten in die Datenbank----------- ####
    ###########################################################################
    def update_videodaten_in_db(self, studio: str, webside_links: str, daten_satz: list) -> Tuple[str, int]:
        errview: str = None        
        anzahl_aktualisiert: int = 0
        webside_link = webside_links.split("\n")[0]

        self.open_database()
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare(f"UPDATE '{studio}' SET Titel=:Titel, WebSideLink=:WebSideLink, Data18Link=:Data18Link, \
                            ThePornDB=:ThePornDB, IAFDLink=:IAFDLink, Performers=:Performers, Alias=:Alias, Action=:Action, SceneCode=:SceneCode, \
                            ProductionDate=:ProDate, Regie=:Regie, Movies=:Movies, Synopsis=:Synopsis, Serie=:Serie, \
                            ReleaseDate=:ReleaseDate, Dauer=:Dauer, Tags=:Tags WHERE ID = :ID") 
                query.bindValue(":ID", daten_satz["ID"])               
                query.bindValue(":Titel",daten_satz["Titel"]) 
                query.bindValue(":IAFDLink",daten_satz["IAFDLink"]) 
                query.bindValue(":Performers",daten_satz["Performers"]) 
                query.bindValue(":Alias",daten_satz["Alias"])
                query.bindValue(":Action",daten_satz["Action"]) 
                query.bindValue(":SceneCode",daten_satz["SceneCode"])
                query.bindValue(":ProDate",daten_satz["ProDate"]) 
                query.bindValue(":Regie",daten_satz["Regie"]) 
                query.bindValue(":Movies",daten_satz["Movies"])
                query.bindValue(":Synopsis",daten_satz["Synopsis"])
                query.bindValue(":Serie",daten_satz["Serie"]) 
                query.bindValue(":ReleaseDate",daten_satz["ReleaseDate"])
                query.bindValue(":Dauer",daten_satz["Dauer"]) 
                query.bindValue(":Tags",daten_satz["Tags"])    
                query.bindValue(":WebSideLink",webside_links)
                query.bindValue(":Data18Link",daten_satz["Data18Link"])
                query.bindValue(":ThePornDB",daten_satz["ThePornDB"])                
                if query.exec():                        
                    anzahl_aktualisiert = query.numRowsAffected()  
                    print(f"update: {anzahl_aktualisiert}")                  
                else:
                    errview = f"'{self.update_videodaten_in_db.__name__}': {query.lastError().text()} (query)" if query.lastError().text() else (errview or f"Link nicht gefunden in dem {studio} ! (query)")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim der Funktion:'{self.update_videodaten_in_db.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview and self.Main is not None:
            self.db_fehler(errview)
        self.close_database()        
        return errview, anzahl_aktualisiert     
    
    
if __name__ == "__main__":
    ScrapingData()  