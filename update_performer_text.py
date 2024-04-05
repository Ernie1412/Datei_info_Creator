from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from contextlib import contextmanager

from config import PERFORMER_DB_PATH

from utils.database_settings import DB_Darsteller

class DATABASE(): 
    
    def open_database(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE",'db_darsteller')
        self.db.setHostName("localhost")        
        self.db.setDatabaseName(PERFORMER_DB_PATH)
        self.db.open()

    @contextmanager
    def managed_query(self):
        query = QSqlQuery(self.db)
        try:
            yield query
        finally:
            query.finish()
            query.clear() 
            del query

    def close_database(self):
        self.db.close()            
        connection_name = self.db.connectionName()
        del self.db
        QSqlDatabase.database(connection_name).close()         
        QSqlDatabase.removeDatabase(connection_name) # Vorhandene Verbindung schließen
    
    
    def check_update_performer(self, studio, performer_data):
        errview: str=None
        artist_id=None
        studio_id=None
        add_url=False
        add_name=False
        update_sex=False
        self.open_database()
        if self.db.isOpen():         
            with self.managed_query() as query:
                query.prepare("SELECT PornSideID, DB_NamesLink.Image, DB_NamesLink.ArtistID, DB_NamesLink.Alias FROM DB_Studio JOIN DB_NamesLink WHERE StudioName=:studio AND DB_NamesLink.Link=:link")
                query.bindValue(":studio", studio) 
                query.bindValue(":link", performer_data["studio_url"])                   
                query.exec() 
                while query.next():
                    studio_id=query.value("PornSideID")
                    image=query.value("DB_NamesLink.Image")
                    artist_id=query.value("DB_NamesLink.ArtistID")
                    alias=query.value("DB_NamesLink.Alias")
                    errview = query.lastError().text() if query.lastError().text() else errview 
                if not studio_id:
                    add_url=True 
                query.prepare("SELECT ArtistID, Geschlecht FROM DB_Artist WHERE Name=:name")
                query.bindValue(":name", performer_data["name"])                                   
                query.exec() 
                while query.next():
                    artist_id=query.value("ArtistID")
                    sex=query.value("Geschlecht") 
                    errview = query.lastError().text() if query.lastError().text() else errview 
                if not artist_id:
                    add_name=True
                else:
                    if sex!=performer_data["sex"]:
                        update_sex=True
                # SELECT MAX(ArtistID) AS MaxArtistID, Name FROM DB_Artist WHERE Name IN (SELECT Name FROM DB_Artist GROUP BY Name HAVING COUNT(*) > 1) GROUP BY Name;
            del query
        self.close_database() 
        return errview, add_url, add_name, update_sex, artist_id

    def add_url_performer(self, studio, artist_id, performer_data): 
        errview: str=None
        self.open_database()
        if self.db.isOpen():         
            with self.managed_query() as query:
                query.prepare("SELECT PornSideID FROM DB_Studio WHERE StudioName=:studio")
                query.bindValue(":studio", studio)
                query.exec()
                if query.next():
                    studio_id=query.value("PornSideID")
                    errview = query.lastError().text() if query.lastError().text() else errview
                else:
                    errview="Kein Studio gefunden in {studio}"
                if not errview:
                    query.prepare("INSERT INTO DB_NamesLink (Link,Image,ArtistID,StudioID,Alias) VALUES (:Link,:Image,:ArtistID,:StudioID,:Alias);")
                    query.bindValue(":Link", performer_data["studio_url"])
                    query.bindValue(":Image", performer_data["image_pfad"])
                    query.bindValue(":ArtistID",artist_id) 
                    query.bindValue(":StudioID", studio_id)
                    query.bindValue(":Alias",performer_data["name"])
                    query.exec()
                    errview = query.lastError().text() if query.lastError().text() else errview
            del query
        self.close_database() 
        return errview    

def performer_data():    
    performer_data={}
    performer_data["name"] = "Alyssia Vera"
    performer_data["studio_url"] = "https://www.bangbrosnetwork.com/model/413901/alyssia-vera"
    performer_data["sex"] = 1
    performer_data["image_pfad"] = "__artists_Images/Addison Avery/[BangBros]-413901.jpg"
    performer_data["iafd_link"] = "https://www.iafd.com/person.rme/perfid=alyssia_hmf_22/gender=f/alyssia-vera.htm"
    return performer_data

def update():
    studio = "BangBros" 
    database_darsteller = DB_Darsteller()
    database_darsteller.update_performer(studio, performer_data())

studio="Mofos"
data_base=DATABASE()

errview, add_url, add_name, update_sex, artist_id = data_base.check_update_performer(studio, performer_data())
print(f"Add Name: {add_name}, Update Sex: {update_sex}")
if not errview:
    if add_url:         
        errview=data_base.add_url_performer(studio, artist_id, performer_data())
        performer=performer_data()
        url=performer["studio_url"]
        print(f"Add: {url} --> {errview}")
    

        