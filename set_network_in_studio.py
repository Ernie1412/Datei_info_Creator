from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from contextlib import contextmanager
from tldextract import extract

from config import SETTINGS_DB_PATH

class Webside_Settings():
    def __init__(self):
        print("BaseClass init")
    
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
        QSqlDatabase.removeDatabase(connection_name)

 ##### ------------ Fehler-Behandlung ---------------- ##########
    ################################################################
    def db_fehler(self, fehler: str) -> None: 
        print(f" --> {fehler}") 


    def set_network_in_studio_alias(self, network: str, studio: str, studio_link:str=None) -> str:
        errview: str = None        
        setting_id: str = None
        setting_id_alias: str = None

        self.open_database()
        if self.db.isOpen():            
            with self.managed_query() as query:                 
                query.prepare("SELECT WebScrapping_Settings.SettingID, Studio_Alias.SettingID FROM WebScrapping_Settings LEFT JOIN Studio_Alias ON Studio_Alias.SettingID = WebScrapping_Settings.SettingID WHERE WebScrapping_Settings.Studio=:studio")  
                query.bindValue(":studio", studio)                   
                query.exec()                                                          
                if query.next():
                    setting_id_alias = query.value('Studio_Alias.SettingID')  
                    setting_id = query.value('WebScrapping_Settings.SettingID')                            
                errview = f"Fehler: {query.lastError().text()} (db) beim der Funktion:'{self.set_network_in_studio_alias.__name__}'" if query.lastError().text() else errview
            if not setting_id:
                with self.managed_query() as query:                 
                    query.prepare("INSERT INTO WebScrapping_Settings (Studio) VALUES (:Studio)")  
                    query.bindValue(":Studio", studio)
                    query.exec() 
                    errview = f"Fehler: {query.lastError().text()} (db) beim der Funktion:'{self.set_network_in_studio_alias.__name__}'" if query.lastError().text() else errview
                with self.managed_query() as query:
                    query.prepare("SELECT LAST_INSERT_ROWID()")                    
                    query.exec()
                    if query.next():
                        setting_id = query.value(0)                    
            if not setting_id_alias:
                with self.managed_query() as query:                 
                    query.prepare("INSERT INTO Studio_Alias (SettingID, Studio, Studio_link, Network_tpdb) VALUES(:SettingID,:Studio,:Studio_link, :Network);") 
                    #studio_link = studio.lower()+".com" 
                    query.bindValue(":Studio", studio)
                    query.bindValue(":Studio_link", studio_link)
                    query.bindValue(":SettingID", setting_id)
                    query.bindValue(":Network", network)                    
                    query.exec()
                    errview = f"Fehler: {query.lastError().text()} (db) beim der Funktion:'{self.set_network_in_studio_alias.__name__}'" if query.lastError().text() else errview
            del query
        if errview:
            self.db_fehler(errview)
        self.close_database()         
        return network 
    
     
    
matchs = {
        '18onlygirlsblog': "All Fine Girls",
        'ultrafilms': "UltraFilms",
        'wowgirlsblog': "WowGirls",
        'wowpornblog': "WowPorn",
    }

for link, studio_name in matchs.items():
    #studio = extract(match).domain
    studio = studio_name.replace(" ", "")
    link = link+".com"
    network = "AdultTime"
    Webside_Settings().set_network_in_studio_alias(network, studio, link)  