from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlField
from PyQt6.QtCore import QDateTime
from contextlib import contextmanager
import json
from typing import List, Tuple

from config import SIDE_DATAS_DB_PATH, DB_RECORD_JSON

class VideoData:

    def __init__(self):        
        self.data = []

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


class DB_WebSide:
   
    def __init__(self, MainWindow = None):
        super().__init__() 
        self.Main = MainWindow 
        QSqlDatabase.removeDatabase('my_connection') # Vorhandene Verbindung schließen
        self.db = QSqlDatabase.addDatabase("QSQLITE",'my_connection')
        self.db.setHostName("localhost")
        self.db.setDatabaseName(SIDE_DATAS_DB_PATH)   

    @contextmanager
    def managed_query(self):
        query = QSqlQuery(self.db)
        try:
            yield query
        finally:
            del query 

    def db_fehler(self,von_welchen_feld: str, db_or_query) -> None:
        fehler: str = None      
        if isinstance(db_or_query, str): 
            fehler=db_or_query
        else:
            fehler=db_or_query.lastError().text()        
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.Main.lbl_db_status.setStyleSheet("background-color : #FA5882")
        self.Main.lbl_db_status.setText(f"Zeit: {current_time} --> Fehler: {fehler} - >{von_welchen_feld}<")


    def hole_link_von_performer(self, performers: str, studio: str) -> str:
        errview = None
        video_data = VideoData()
        
        self.db.open()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT Titel, WebSideLink, IAFDLink, Performers, Alias, Action, ReleaseDate, ProductionDate, Serie, Regie, SceneCode, Dauer, Movies, Synopsis, Tags FROM {studio} WHERE Performers LIKE :Performers;")
                query.bindValue(":Performers", f"%{performers}%")
                query.exec()                
                while query.next():
                    video_data.initialize(query.record())                    
                if not video_data.data:
                    errview = f"Keine Daten für {performers} gefunden"
        else:
            self.db_fehler("beim Suchen des Performers", "db")

        self.db.close()

        video_data.save_to_json()        
        return errview
    
    def webside_db_daten(self,link,studio):
    ### Daten anhand des BangBros links aus DB nehmen für Such Maske ### 
        errview=""        
        self.db.open()            
        if self.db.isOpen():
            with self.managed_query() as query:            
                query.prepare(f"SELECT Titel,ReleaseDate,Serie,SceneCode,Dauer,Performers FROM {studio} WHERE INSTR(LOWER(WebSideLink), LOWER(:Link)) = 1")
                query.bindValue(":Link",link)
                query.exec()
                if query.next():
                    titel=query.value("Titel")
                    if titel=="": 
                        self.Main.lbl_datenbank_titel.setStyleSheet("background-color : red")                       
                    self.Main.lbl_datenbank_titel.setText(titel)
                    release_date=query.value("ReleaseDate")
                    if titel=="": 
                        self.Main.lnEdit_IAFDURL.setStyleSheet("background-color : red")
                    self.Main.lnEdit_IAFDURL.setText(release_date)
                    serie=query.value("Serie")
                    if serie=="": 
                        self.Main.lbl_SuchNebenSide.setStyleSheet("background-color : red")
                    self.Main.lbl_SuchNebenSide.setText(serie) 
                errview=query.lastError().text()
                if errview!="":
                    self.db_fehler("beim Daten holen",query)
        else:
            self.db_fehler("beim Daten holen",self.db)
        self.db.close()
        return errview  
        
    def hole_link_aus_db(self, link: str, studio: str) -> str:
        errview = None
        video_data = VideoData()

        self.db.open()            
        if self.db.isOpen(): 
            with self.managed_query() as query:
                query.prepare(f"SELECT * FROM {studio} WHERE INSTR(LOWER(WebSideLink), LOWER(:Link)) = 1;")
                query.bindValue(":Link", link)
                query.exec()
                if query.next():
                    video_data.initialize(query.record())
                if not video_data.data:
                    errview = f"Keine Daten für {link} gefunden"
        else:
            self.db_fehler("beim Suchen des Links", self.db)

        self.db.close()

        video_data.save_to_json()
        return errview

    
    def hole_data18link_von_db(self, webside_link: str, studio: str) -> str:        
        data18_link: str = None
        
        self.db.open()            
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT Data18Link FROM {studio} WHERE INSTR(LOWER(WebSideLink), LOWER(:WebSideLink)) = 1")
                query.bindValue(":WebSideLink",webside_link)
                query.exec()
                if query.next():
                    data18_link=query.value("Data18Link")
                    if query.lastError().text():
                        self.db_fehler(f"beim {studio} holen",query)         
        else:
            self.db_fehler(f"beim Data18Link holen",self.db)
        self.db.close()
        return data18_link
    
    def hole_dauer_von_db(self,webside_link,studio):        
        dauer=""
        self.db.open()            
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT Dauer FROM {studio} WHERE INSTR(LOWER(WebSideLink), LOWER(:Link)) = 1")
                query.bindValue(":Link",webside_link)
                query.exec()
                if query.next():
                    dauer=query.value("Dauer")
                    if query.lastError().text()!="":
                        self.db_fehler(f"beim Dauer holen",query)           
        else:
            self.db_fehler("beim Dauer holen",self.db)
        self.db.close()
        return dauer
        
    def hole_titel_aus_db(self, titel: str,studio: str) -> str:           
        errview: str = None 
        video_data = VideoData()        
        self.db.open()            
        if self.db.isOpen():            
            with self.managed_query() as query:
                if titel == "*":
                    titel = ""
                query.prepare(f"SELECT * FROM {studio} WHERE Titel LIKE :titel")                
                query.bindValue(":titel", f"%{titel}%")
                query.exec()                 
                while query.next():
                    video_data.initialize(query.record())
                if not video_data.data:
                    errview = f"Keine Daten für {titel} gefunden"
        else:
            self.db_fehler("beim Suchen des Titels", "db")

        self.db.close()

        video_data.save_to_json()
        return errview 

    def hole_webside_movies(self,link,studio):
        errview,movies=("","")     
        self.db.open()            
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT Movies FROM {studio} WHERE INSTR(LOWER(WebSideLink), LOWER(:Link)) = 1;")
                query.bindValue(":Link", link)
                query.exec()
                if query.next():
                    movies=query.value("Movies") 
                    if movies!="":
                        movies=movies.split("\n")               
                errview=query.lastError().text()
                if query.lastError().text()!="":
                        self.db_fehler("beim Movies holen",query) 
        else:
            self.db_fehler("beim Movies holen",self.db)
        self.db.close()
        return errview,movies 
    
    def add_neue_videodaten_in_db(self, studio, webside_link, daten_satz: list):             
        errview: str = None
        farbe: str = '#F78181'
        isneu: int = 0
        fields = {
            "Titel": daten_satz["Titel"],
            "WebSideLink": daten_satz["WebSideLink"],
            "Data18Link": daten_satz["Data18Link"],
            "IAFDLink": daten_satz["IAFDLink"],
            "ReleaseDate": daten_satz["ReleaseDate"],
            "Dauer": daten_satz["Dauer"],
            "Performers": daten_satz["Performers"],
            "Alias": daten_satz["Alias"],
            "Action": daten_satz["Action"],
            "Synopsis": daten_satz["Synopsis"],
            "Tags": daten_satz["Tags"],
            "Serie": daten_satz["Serie"],
            "SceneCode": daten_satz["SceneCode"]
                }
        self.db.open()            
        if self.db.isOpen():
            with self.managed_query() as query: 
                query.prepare(f'INSERT INTO "{studio}" (ID, Titel, WebSideLink, Data18Link, IAFDLink, ReleaseDate, Dauer, Performers, \
                    Alias, Action, Synopsis, Tags, Serie, SceneCode) VALUES (NULL, :Titel, :WebSideLink, :Data18Link, :IAFDLink, \
                    :ReleaseDate, :Dauer, :Performers, :Alias, :Action, :Synopsis, :Tags, :Serie, :SceneCode)')                        
                driver = self.db.driver()                        
                for field_name, value in fields.items():
                    field = QSqlField("text")
                    field.setValue(value)
                    query.bindValue(f":{field_name}", driver.formatValue(field, False))

                query.exec()
                errview = query.lastError().text()
                if not errview:                         
                    farbe='#00FF40'
                    isneu=1          

        else:
            self.db_fehler(f"Fehler beim Adden von neuen Daten: bei {webside_link}",self.db)
        self.db.close()
        return errview , farbe, isneu
    
    def update_videodaten_in_db(self, studio, webside_links, daten_satz: list):
        errview: str = None        
        anzahl_aktualisiert: int = 0
        webside_link = webside_links.split("\n")[0]

        self.db.open()            
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare(f'SELECT ID FROM {studio} WHERE (LOWER(IAFDLink) IS NOT NULL AND LOWER(IAFDLink) = LOWER(:IAFDLink)) OR (LOWER(Data18Link) IS NOT NULL AND LOWER(Data18Link) = LOWER(:Data18Link)) OR (INSTR(LOWER(WebSideLink), LOWER(:WebSideLink)) = 1) OR (LOWER(Titel) = LOWER(:Titel));')
                query.bindValue(":WebSideLink",webside_link) 
                query.bindValue(":IAFDLink",daten_satz["IAFDLink"])
                query.bindValue(":Data18Link",daten_satz["Data18Link"])
                query.bindValue(":Titel",daten_satz["Titel"])
                query.exec()                                           
                if query.next():
                    webside_id=query.value("ID")
                    with self.managed_query() as query:              
                        query.prepare(f'UPDATE "{studio}" SET Titel=:Titel, WebSideLink=:WebSideLink, Data18Link=:Data18Link, \
                            IAFDLink=:IAFDLink, Performers=:Performers, Alias=:Alias, Action=:Action, SceneCode=:SceneCode, \
                            ProductionDate=:ProDate, Regie=:Regie, Movies=:Movies, Synopsis=:Synopsis, Serie=:Serie, \
                            ReleaseDate=:ReleaseDate, Dauer=:Dauer, Tags=:Tags WHERE ID = :ID') 
                        query.bindValue(":ID",webside_id)               
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
                        query.exec()
                        errview = query.lastError().text()
                        anzahl_aktualisiert = query.numRowsAffected()
                        if errview:
                            self.db_fehler(f"beim updaten von Datensatz: {webside_link}",query)
                else:                    
                    errview = "Link nicht gefunden !"
        else:
            self.db_fehler(f"beim updaten von Datensatz: {webside_link}",self.db)
        self.db.close()
        return errview, anzahl_aktualisiert  

    def is_link_in_db(self,webside_link=None,iafdlink=None):        
        self.db.open()               
        if self.db.isOpen():
            tables=self.db.tables()                     
            for table in tables: 
                if table in ['sqlite_sequence', 'Movies', 'Studios', 'Videos', 'AliasTable']:
                    continue                   
                with self.managed_query() as query: 
                    query.prepare(f"SELECT * FROM {table} WHERE LOWER(WebSideLink) LIKE :Link OR IAFDLink=:IAFDLink")
                    query.bindValue(":Link", f"%{webside_link}%")
                    query.bindValue(":IAFDLink", iafdlink)                
                    query.exec()                    
                    if query.lastError().text():
                        self.db_fehler("beim Linküberprüfung",query)                           
                    if query.next():
                        self.db.close()                                                   
                        return True, webside_link            
        else:
            self.db_fehler("beim Linküberprüfung (is Link in DB)",self.db)
        self.db.close()        
        return False, webside_link

    def is_studio_in_db(self, studio: str) -> bool:        
        isin: bool = False

        self.db.open()
        if self.db.isOpen():
            tables=self.db.tables()        
            if studio in tables:
                isin = True 
        else:
            self.db_fehler("beim Linküberprüfung (Studio)",self.db)
        self.db.close()        
        return isin  
    
    def from_link_to_studio(self, link: str) -> str:
        studio: str = None

        self.db.open()            
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare(f'SELECT Studio FROM AliasTable WHERE LOWER(Links) LIKE :WebSideLink;')
                query.bindValue(":WebSideLink",f"%{link}%")                
                query.exec()
                if query.lastError().text():
                    self.db_fehler("von link zum Studio Überprüfung (query)",query)                                           
                if query.next():
                    studio = query.value("Studio")
        else:
            self.db_fehler("von Link zum Studio Überprüfung (db)",self.db)
        self.db.close()        
        return studio    

    
if __name__ == "__main__":
    DB_WebSide()  