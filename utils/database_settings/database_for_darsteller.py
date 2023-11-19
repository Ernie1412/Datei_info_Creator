from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtCore import QDateTime
from contextlib import contextmanager
from typing import Tuple, Optional

from config import PERFORMER_DB_PATH


class DB_Darsteller:

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
                command += " AND ArtistID IN (SELECT ArtistID FROM DB_NamesLink INNER JOIN DB_Studio ON DB_NamesLink.PornSideID = \
                            DB_Studio.PornSideID WHERE StudioName = :studio)"
            with self.managed_query() as query:
                query.prepare(command)
                query.bindValue(":Performername", name)
                query.bindValue(":studio", studio)
                query.exec()       
                if query.next():                    
                    sex = query.value("Geschlecht")                       
                    is_vorhanden = True
                    errview = f"kein {name} gefunden in der Datenbank" if not query.lastError().text() and not is_vorhanden else query.lastError().text()
                else:
                    errview = f"'{self.isdaDarsteller.__name__}': {query.lastError().text()} (query)" if query.lastError().text() else (errview or f"kein {name} gefunden in der Datenbank")
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.isdaDarsteller.__name__}'" if self.db.lastError().text() else errview          
            
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return is_vorhanden, sex 
    ############################################################################################ 
    ###------------------------ Daten in die Datenbank adden ------------------------------- ###
    ############################################################################################
    def addDarsteller_in_db(self,performer_data: dict, studio: str=None) -> tuple[int, int, int]:
        errview: str=None
        artist_neu: int=0
        sex_neu: int=0
        link_neu: int=0

        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager            
            with self.managed_query() as query:
                # Überprüfen, ob das Studio in der Datenbank vorhanden ist
                query.prepare("SELECT PornSideID FROM DB_Studio WHERE StudioName=:StudioName;")
                query.bindValue(":StudioName", studio)
                query.exec()
                if query.next():
                    studio_id = query.value('PornSideID')
                    errview = query.lastError().text() if query.lastError().text() else None
                else:
                    # Wenn das Studio nicht in der DB ist, neu hinzufügen und die ID abrufen
                    with self.managed_query() as query:
                        query.prepare("INSERT INTO DB_Studio (StudioName) VALUES (:StudioName);")
                        query.bindValue(":StudioName", studio)
                        query.exec()
                        errview = query.lastError().text() if query.lastError().text() else errview
                    with self.managed_query() as query:
                        query.prepare("SELECT MAX(PornSideID) FROM DB_Studio;")
                        query.exec()
                        query.next()
                        studio_id = query.value('MAX(PornSideID)')
                        errview = query.lastError().text() if query.lastError().text() else errview
                # Überprüfen und aktualisieren Sie Geschlecht und Nation
                with self.managed_query() as query:
                    query.prepare("SELECT ArtistID, Geschlecht, Nation FROM DB_Artist WHERE Name=:Name;")
                    query.bindValue(":Name", performer_data["Name"])
                    query.exec()
                    errview = query.lastError().text() if query.lastError().text() else errview
                    if query.next():                        
                        artist_id = query.value('ArtistID')
                        db_geschlecht = query.value('Geschlecht')
                        db_nation = query.value('Nation')
                        errview = query.lastError().text() if query.lastError().text() else errview
                        # Geschlecht und Nation aktualisieren, wenn erforderlich
                        with self.managed_query() as query:
                            query.prepare("UPDATE DB_Artist SET Geschlecht=IFNULL(:Geschlecht, Geschlecht), "
                                        "Nation=IFNULL(:Nation, Nation) WHERE ArtistID=:ArtistID;")
                            query.bindValue(":Geschlecht", performer_data["Geschlecht"])
                            query.bindValue(":Nation", performer_data["Nation"])
                            query.bindValue(":ArtistID", artist_id)
                            query.exec()
                            sex_neu += 1
                            errview = query.lastError().text() if query.lastError().text() else errview
                    else:
                        # Wenn der Künstler nicht vorhanden ist, legen Sie ihn neu an
                        with self.managed_query() as query:                            
                            query.prepare("INSERT INTO DB_Artist (ArtistID, Name, Geschlecht, Nation) "
                                        "VALUES (NULL, :Name, :Geschlecht, :Nation);")
                            query.bindValue(":Name", performer_data["Name"])
                            query.bindValue(":Geschlecht", performer_data["Geschlecht"])
                            query.bindValue(":Nation", performer_data["Nation"])
                            query.exec()
                            errview = query.lastError().text() if query.lastError().text() else errview
                        # Holen Sie die zugehörige ID ab
                        with self.managed_query() as query:                            
                            query.prepare("SELECT max(ArtistID) FROM DB_Artist;")
                            query.exec()
                            query.next()
                            artist_id = query.value('max(ArtistID)')
                            errview = query.lastError().text() if query.lastError().text() else errview
                        artist_neu = 1
                    # Wenn der Künstler neu ist oder Informationen fehlen, fügen Sie NamesLink hinzu
                    if artist_neu == 1 or (performer_data["ArtistLink"] or performer_data["ImagePfad"]) is not None:
                        with self.managed_query() as query:                            
                            query.prepare("INSERT INTO DB_NamesLink (NamesID, Link, Image, ArtistID, PornSideID) "
                                        "VALUES (NULL, IFNULL(:Link, ''), IFNULL(:Image, ''), :ArtistID, :PornSideID);")
                            query.bindValue(":Link", performer_data["ArtistLink"])
                            query.bindValue(":Image", performer_data["ImagePfad"])
                            query.bindValue(":ArtistID", artist_id)
                            query.bindValue(":PornSideID", studio_id)
                            query.exec()
                            errview = query.lastError().text() if query.lastError().text() else errview
                        link_neu += 1
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.add_neue_videodaten_in_db.__name__}'" if self.db.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()
        return artist_neu, sex_neu, link_neu
    
    def add_db_artistlink(self,artistname,link=None,studio=None):
        errview: str=None 
        neu: int=0
        artist_id: int=0
        studio_id: int=0

        self.open_database()
        if self.db.isOpen():  # öffnet die datenbank mit einem contex Manager        
            with self.managed_query() as query:
                query.prepare("SELECT ArtistID,Link FROM DB_NamesLink WHERE ArtistID IN (SELECT ArtistID FROM DB_Artist WHERE Name = :Name);")
                query.bindValue(":Name",artistname)
                query.exec()        
                if query.next(): 
                    artist_id=query.value("ArtistID")
                    link=query.value("Link")
                else:
                    neu=1
                    with self.managed_query() as query:
                        query.prepare("INSERT INTO DB_NamesLink (NamesID,Link,ArtistID) VALUES (NULL,:Link,:ArtistID);")
                        query.bindValue(":Link",link)
                        query.bindValue(":ArtistID",artist_id)
                        query.exec()
                        name_neu+=1
                        if studio is not None:
                            with self.managed_query() as query:
                                query.prepare("SELECT PornSideID FROM DB_Studio WHERE StudioName = :StudioName")
                                query.bindValue(":StudioName",studio)
                                query.exec()
                                studio_id=query.value("PornSideID")
                        else:
                            with self.managed_query() as query:
                                query.prepare("INSERT INTO DB_Studio (PornSideID, StudioName) VALUES (NULL,:StudioName;")
                                query.bindValue(":StudioName",studio)
                                query.exec()
                                query.prepare("SELECT MAX(PornSideID) FROM DB_Studio;")
                                query.exec()
                                if query.next():
                                    artist_id=query.value('MAX(PornSideID)')                                
                        if link is not None: ###  link von hole_db_artistlink   ###
                            with self.managed_query() as query:
                                query.prepare("INSERT INTO DB_NamesLink (NamesID,Link,ArtistID,PornSideID) VALUES (NULL, :Link, :ArtistID, :PornSideID);")   
                                query.bindValue(":Link",link)
                                query.bindValue(":ArtistID",artist_id)
                                query.bindValue(":PornSideID",studio_id)
                                query.exec()
                                name_neu+=1 
                                errview = query.lastError().text() if query.lastError().text() else errview    
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.add_db_artistlink.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return neu

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
                        query.prepare("INSERT INTO DB_Movies (MovieID,PornSideID,VideoTitel,VideoLink,Dauer,Resize,Bitrate,\
                            Ursprung,ArtistID,Tags,Beschreibung,ReleaseDate,DownloadDate,DateiGroesse,Regie,MovieTitel,FilmLink,\
                            HDDLink) VALUES (NULL,{movie_id},'{VideoTitel}','{VideoLink}','{Dauer}','{Resize}',{Bitrate},\
                            '{Ursprung}','{ArtistID}','{Tags}','{Beschreibung}','{ReleaseDate}','{DownloadDate}',{DateiGroesse},\
                            '{Regie}','{MovieTitel}','{FilmLink}','{HDDLink}');")
                        query.bindValue(":PornSideID",movie_id)
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
                query.prepare("SELECT PornSideID, StudioName, Homepage FROM DB_Studio WHERE StudioName = :StudioName OR \
                            Homepage = :Homepage")
                query.bindValue(":StudioName", studio)
                query.bindValue(":Homepage", homepage)
                query.exec()        
                if query.next():            
                    studio_id=query.value("PornSideID")
                    neu,studio=(1, self.query.value("StudioName")) if studio == ("" or self.query.value("StudioName")) else (0, studio)
                    neu,homepage=(1, self.query.value("Homepage")) if homepage == ("" or self.query.value("Homepage")) else (0, homepage)                
                if neu==1:   ### -------- Wenn kein Link da ist, dann Update --------- ### 
                    with self.managed_query() as query:
                        query.prepare("UPDATE DB_Studio SET StudioName = :StudioName, Homepage = :Homepage WHERE PornSideID = :PornSideID")
                        query.bindValue(":StudioName", studio)
                        query.bindValue(":Homepage", homepage) 
                        query.bindValue(":PornSideID", studio_id)                
                        query.exec()                
                else:
                    if studio_id==None:
                        with self.managed_query() as query:
                            query.prepare("INSERT INTO DB_Studio (PornSideID, StudioName, Homepage) VALUES (NULL,:StudioName,:Homepage)")
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
                query.prepare("SELECT PornSideID FROM DB_Studio WHERE StudioName= :StudioName;")
                query.bindValue(":StudioName",studio)
                query.exec()
                if self.query.next():
                    studio_id=query.value("PornSideID")
                    errview = query.lastError().text() if query.lastError().text() else errview
            with self.managed_query() as query:
                query.prepare("SELECT DB_Artist.ArtistID,RassenID FROM DB_Artist INNER JOIN DB_NamesLink ON DB_Artist.ArtistID \
                    = DB_NamesLink.ArtistID INNER JOIN DB_Studio ON DB_Studio.PornSideID = DB_NamesLink.PornSideID \
                    WHERE DB_Studio.PornSideID=:PornSideID And Geschlecht=:Geschlecht;")
                query.bindValue(":PornSideID",studio_id)
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
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.set_black_people.__name__}'" if self.db.lastError().text() else errview          
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()        
        return neu
        
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
                    DB_Artist.ArtistID = DB_NamesLink.ArtistID INNER JOIN DB_Studio ON DB_Studio.PornSideID \
                    = DB_NamesLink.PornSideID WHERE Name = :Name and StudioName = :StudioName;")
                query.bindValue(":Name",artistname)
                query.bindValue(":StudioName",studio) 
                query.exec()        
                if query.next():                
                    link=query.value("DB_NamesLink.Link")
                    errview = f"keine Links für {artistname} gefunden" if not query.lastError().text() and not link else query.lastError().text()
                else:
                    errview = f"'{self.hole_db_artistlink.__name__}': {query.lastError().text()} (query)" if query.lastError().text() else (errview or f"keine Links für {artistname} gefunden")    
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.hole_db_artistlink.__name__}'" if self.db.lastError().text() else errview          
            del query
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
            errview = f"Fehler: {self.db.lastError().text()} (db) beim öffnen von Funktion:'{self.get_performers_picture.__name__}'" if self.db.lastError().text() else errview          
            del query
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

if __name__ == "__main__":
    DB_Darsteller()