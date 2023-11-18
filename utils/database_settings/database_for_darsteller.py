from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from contextlib import contextmanager
from typing import Tuple

from config import PERFORMER_DB_PATH

class DB_Darsteller:

    def __init__(self, MainWindow):
        self.Main = MainWindow        
        QSqlDatabase.removeDatabase('my_connection') # Vorhandene Verbindung schließen
        self.db= QSqlDatabase.addDatabase("QSQLITE",'my_connection')
        self.db.setHostName("localhost")        
        self.db.setDatabaseName(PERFORMER_DB_PATH) 

    @contextmanager
    def managed_query(self):
        query = QSqlQuery(self.db)
        try:
            yield query
        finally:
            # Schließen Sie die QSqlQuery-Instanz
            query.finish()
            query.clear()
            del query

    def db_fehler(self):
        self.Main.lbl_db_status.setStyleSheet("background-color : #FA5882")
        self.Main.lbl_db_status.setText(f"Fehler: {self.db.lastError().text()}")

    
    def addDarsteller_in_db(self, name: str, geschlecht: int=0, studio: str=None, ArtistLink: str=None, ImagePfad: str=None, nation: str=None) -> tuple[int, int, int]:
        artist_neu, sex_neu, link_neu = 0, 0, 0
        self.db.open()

        if self.db.isOpen():
            with self.managed_query() as query:
                # Überprüfen, ob das Studio in der Datenbank vorhanden ist
                query.prepare("SELECT PornSideID FROM DB_PornSide WHERE PornSideName=:PornSideName;")
                query.bindValue(":PornSideName", studio)
                query.exec()

                if query.next():
                    studio_id = query.value('PornSideID')
                else:
                    # Wenn das Studio nicht in der DB ist, neu hinzufügen und die ID abrufen
                    with self.managed_query() as query:
                        query.prepare("INSERT INTO DB_PornSide (PornSideName) VALUES (:PornSideName);")
                        query.bindValue(":PornSideName", studio)
                        query.exec()
                    with self.managed_query() as query:
                        query.prepare("SELECT max(PornSideID) FROM DB_PornSide;")
                        query.exec()
                        query.next()
                        studio_id = query.value('max(PornSideID')

                # Überprüfen und aktualisieren Sie Geschlecht und Nation
                with self.managed_query() as query:
                    query.prepare("SELECT ArtistID, Geschlecht, Nation FROM DB_Artist WHERE Name=:Name;")
                    query.bindValue(":Name", name)
                    query.exec()

                    if query.next():
                        artist_id = query.value('ArtistID')
                        db_geschlecht = query.value('Geschlecht')
                        db_nation = query.value('Nation')

                        # Geschlecht und Nation aktualisieren, wenn erforderlich
                        with self.managed_query() as query:
                            query.prepare("UPDATE DB_Artist SET Geschlecht=IFNULL(:Geschlecht, Geschlecht), "
                                        "Nation=IFNULL(:Nation, Nation) WHERE ArtistID=:ArtistID;")
                            query.bindValue(":Geschlecht", geschlecht)
                            query.bindValue(":Nation", nation)
                            query.bindValue(":ArtistID", artist_id)
                            query.exec()
                            sex_neu += 1

                    else:
                        # Wenn der Künstler nicht vorhanden ist, legen Sie ihn neu an
                        with self.managed_query() as query:
                            query.prepare("INSERT INTO DB_Artist (ArtistID, Name, Geschlecht, Nation) "
                                        "VALUES (NULL, :Name, :Geschlecht, :Nation);")
                            query.bindValue(":Name", name)
                            query.bindValue(":Geschlecht", geschlecht)
                            query.bindValue(":Nation", nation)
                            query.exec()

                        # Holen Sie die zugehörige ID ab
                        with self.managed_query() as query:
                            query.prepare("SELECT max(ArtistID) FROM DB_Artist;")
                            query.exec()
                            query.next()
                            artist_id = query.value('max(ArtistID)')
                        artist_neu = 1

                    # Wenn der Künstler neu ist oder Informationen fehlen, fügen Sie NamesLink hinzu
                    if artist_neu == 1 or (ArtistLink or ImagePfad) is not None:
                        with self.managed_query() as query:
                            query.prepare("INSERT INTO DB_NamesLink (NamesID, Link, Image, ArtistID, PornSideID) "
                                        "VALUES (NULL, IFNULL(:Link, ''), IFNULL(:Image, ''), :ArtistID, :PornSideID);")
                            query.bindValue(":Link", ArtistLink)
                            query.bindValue(":Image", ImagePfad)
                            query.bindValue(":ArtistID", artist_id)
                            query.bindValue(":PornSideID", studio_id)
                            query.exec()
                        link_neu += 1

        self.db.close()
        return artist_neu, sex_neu, link_neu
    
    
    def isdaDarsteller(self, name: str, studio: str=None) -> Tuple[bool, int]:
        is_vorhanden: bool=False
        sex: int = 0

        self.db.open()
        if self.db.isOpen():            
            command = "SELECT Geschlecht FROM DB_Artist WHERE Name = :Performername"
            if studio:
                command += " AND ArtistID IN (SELECT ArtistID FROM DB_NamesLink INNER JOIN DB_PornSide ON DB_NamesLink.PornSideID = \
                            DB_PornSide.PornSideID WHERE PornSideName = :studio)"
            with self.managed_query() as query:
                query.prepare(command)
                query.bindValue(":Performername", name)
                query.bindValue(":studio", studio)
                query.exec()       
                if query.next():
                    errview=query.lastError().text()
                    sex = query.value("Geschlecht")                       
                    is_vorhanden = True
                else:
                    errview=query.lastError().text()
        else:
            self.db_fehler()
        self.db.close()
        return is_vorhanden, sex
    
    def WebsideInfos(self,name,homepage):        
        neu,add,studio_id=(0,0,None)
        self.db.open()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT PornSideID, PornSideName, Homepage FROM DB_PornSide WHERE PornSideName = :PornSideName OR \
                            Homepage = :Homepage")
                query.bindValue(":PornSideName", name)
                query.bindValue(":Homepage", homepage)
                query.exec()        
                if query.next():            
                    studio_id=query.value("PornSideID")
                    neu,name=(1, self.query.value("PornSideName")) if name == ("" or self.query.value("PornSideName")) else (0, name)
                    neu,homepage=(1, self.query.value("Homepage")) if homepage == ("" or self.query.value("Homepage")) else (0, homepage)                
                if neu==1:   ### -------- Wenn kein Link da ist, dann Update --------- ### 
                    with self.managed_query() as query:
                        query.prepare("UPDATE DB_PornSide SET PornSideName = :PornSideName, Homepage = :Homepage WHERE PornSideID = :PornSideID")
                        query.bindValue(":PornSideName", name)
                        query.bindValue(":Homepage", homepage) 
                        query.bindValue(":PornSideID", studio_id)                
                        query.exec()                
                else:
                    if studio_id==None:
                        with self.managed_query() as query:
                            query.prepare("INSERT INTO DB_PornSide (PornSideID, PornSideName, Homepage) VALUES (NULL,:PornSideName,:Homepage)")
                            query.bindValue(":PornSideName", name)
                            query.bindValue(":Homepage", homepage)   
                            query.exec()
                            add=1
        else:
            self.db_fehler()
        self.db.close()
        return neu,add

    def add_db_artistlink(self,artistname,link=None,studio=None):
        neu,artist_id,studio_id=(0,0,0)
        self.db.open()
        if self.db.isOpen():        
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
                                query.prepare("SELECT PornSideID FROM DB_PornSide WHERE PornSideName = :PornSideName")
                                query.bindValue(":PornSideName",studio)
                                query.exec()
                                studio_id=query.value("PornSideID")
                        else:
                            with self.managed_query() as query:
                                query.prepare("INSERT INTO DB_PornSideName (PornSideID,PornSideName) VALUES (NULL,:PornSideName;")
                                query.bindValue(":PornSideName",studio)
                                query.exec()
                                query.prepare("SELECT max(PornSideID) FROM DB_PornSide;")
                                query.exec()
                                if query.next():
                                    artist_id=query.value('max(PornSideID)')                                
                        if link is not None: ###  link von hole_db_artistlink   ###
                            with self.managed_query() as query:
                                query.prepare("INSERT INTO DB_NamesLink (NamesID,Link,ArtistID,PornSideID) VALUES (NULL, :Link, :ArtistID, :PornSideID);")   
                                query.bindValue(":Link",link)
                                query.bindValue(":ArtistID",artist_id)
                                query.bindValue(":PornSideID",studio_id)
                                query.exec()
                                name_neu+=1 
        else:
            self.db_fehler()
        self.db.close()
        return neu
    
    def set_black_people(self,studio,Geschlecht):
        artist_ids,neu=([],0)
        self.db.open()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT PornSideID FROM DB_PornSide WHERE PornSideName= :PornSideName;")
                query.bindValue(":PornSideName",studio)
                query.exec()
                if self.query.next():
                    studio_id=query.value("PornSideID")
            with self.managed_query() as query:
                query.prepare("SELECT DB_Artist.ArtistID,RassenID FROM DB_Artist INNER JOIN DB_NamesLink ON DB_Artist.ArtistID \
                    = DB_NamesLink.ArtistID INNER JOIN DB_PornSide ON DB_PornSide.PornSideID = DB_NamesLink.PornSideID \
                    WHERE DB_PornSide.PornSideID=:PornSideID And Geschlecht=:Geschlecht;")
                query.bindValue(":PornSideID",studio_id)
                query.bindValue(":Geschlecht",Geschlecht)
                query.exec()        
                while query.next():                
                    artist_id=query.value("DB_Artist.ArtistID")
                    rassen_id=query.value("RassenID")
                    if rassen_id=="":
                        artist_ids.append(artist_id)
                for artist_id in artist_ids:
                    with self.managed_query() as query:
                        query.prepare("UPDATE DB_Artist SET RassenID=:RassenID WHERE ArtistID=:ArtistID;")
                        query.bindValue(":RassenID",3)
                        query.bindValue(":ArtistID",artist_id)
                        query.exec()
                        neu+=1
        else:
            self.db_fehler()
        self.db.close()
        return neu

    def addMovie(self,PornSide,VideoTitel,VideoLink,Dauer,Resize,Bitrate,Ursprung,ArtistID,Tags,Beschreibung,ReleaseDate,DownloadDate,DateiGroesse,Regie,MovieTitel,FilmLink,HDDLink):
        artist_ids,neu=([],0)
        self.db.open()
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare("SELECT MovieID FROM DB_Movies WHERE VideoTitel=:VideoTitel AND HDDLink=:HDDLink;")
                query.bindValue(":VideoTitel",VideoTitel)
                query.bindValue(":HDDLink",HDDLink)
                if query.next():
                    movie_id=query.value("MovieID")
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
        else:
            self.db_fehler()
        self.db.close()

    def hole_db_artistlink(self,artistname,studio):
        link=None
        self.db.open()
        if self.db.isOpen():        
            with self.managed_query() as query:
                query.prepare("SELECT Geschlecht,DB_NamesLink.Link FROM DB_Artist INNER JOIN DB_NamesLink ON \
                    DB_Artist.ArtistID = DB_NamesLink.ArtistID INNER JOIN DB_PornSide ON DB_PornSide.PornSideID \
                    = DB_NamesLink.PornSideID WHERE Name = :Name and PornSideName = :PornSideName;")
                query.bindValue(":Name",artistname)
                query.bindValue(":PornSideName",studio) 
                query.exec()        
                if query.next():                
                    link=query.value("DB_NamesLink.Link")
        else:
            self.db_fehler()
        self.db.close()
        return link

    def suche_nach_artistname(self,artistname):
        name=[]
        try:
            self.db.open()
        except Exception as e:
            print("Fehler beim Öffnen der Datenbank:", e)
        if self.db.isOpen():               
            with self.managed_query() as query:
                query.prepare("SELECT Name FROM DB_Artist WHERE Name Like :Name_ OR Name=:Name;")
                query.bindValue(":Name_",f'{artistname} %')
                query.bindValue(":Name",artistname)
                query.exec()                
                while query.next():
                    name.append(query.value('Name')) 
        else:
            self.db_fehler()
        self.db.close()        
        return name
    
    def get_performers_picture(self, performer_name: str) -> Tuple[str, list, list]:
        errorview: str= None 
        images: list=[]
        links: list=[]

        self.db.open()
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare('SELECT DB_NamesLink.Image, DB_NamesLink.Link FROM DB_Artist JOIN DB_NamesLink ON DB_Artist.ArtistID = DB_NamesLink.ArtistID WHERE DB_Artist.Name = :Name;')
                query.bindValue(":Name",performer_name)                
                query.exec()                           
                while query.next():
                    images.append(query.value("DB_NamesLink.Image"))
                    links.append(query.value("DB_NamesLink.Link"))
                    errorview = query.lastError().text()
                    if errorview:
                        self.db_fehler("Fehler beim Performer Images Holen (query)",query)                    
            if not images and errorview:
                errorview = "kein Eintrag gefunden !"
        else:
            self.db_fehler("Fehler beim Performer Images Holen (db)",self.db)
        self.db.close()        
        return errorview, images, links 

if __name__ == "__main__":
    DB_Darsteller()