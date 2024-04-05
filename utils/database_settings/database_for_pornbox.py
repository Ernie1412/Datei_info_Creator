from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtCore import QDateTime
from contextlib import contextmanager

from config import SIDE_DATAS_DB_PATH

class PornBoxLinks:
   
    def __init__(self, MainWindow=None):
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

    def db_fehler(self,fehler):          
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        if fehler:            
            self.Main.lbl_db_status.setStyleSheet("background-color : #FA5882")
        self.Main.lbl_db_status.setText(f"{current_time} --> {fehler}")

    def hole_links_von_PornWorld(self, letter, data18_link, tpdb_link, iafd_link, movie):        
        ### nach Titel Suche, soll der Link in Tabelle geschreiben werden ###   
        pornworld: str=None; pornworld_id: int=0
        legalporno: str=None; legalporno_id: int=0
        analvids: str=None; analvids_id: int=0
        ddfmodels: str=None; ddfmodels_id: int=0
               
        self.db.open()            
        if self.db.isOpen():
            with self.managed_query() as query:
                query.prepare(f"SELECT ID, Titel, WebSideLink, Data18Link, ThePornDB, IAFDLink, Dauer FROM PornWorld WHERE Titel LIKE :letter;")
                query.bindValue(":letter",f"%{letter}%")
                query.exec() 
                if query.next():
                    self.Main.txtEdit_Clipboard.setText(query.value("Titel")+"\n---------------------------")
                    pornworld = query.value("WebSideLink").split("\n")[0] if query.value("WebSideLink") else "\n"                                        
                    pornworld_id = query.value("ID")  
            with self.managed_query() as query:
                query.prepare(f"SELECT ID, WebSideLink FROM LegalPorno WHERE WebSideLink LIKE :letter;")
                query.bindValue(":letter",f"%{letter}%")
                query.exec() 
                if query.next():
                    legalporno=query.value("WebSideLink").split("\n")[0]
                    legalporno_id = query.value("ID") 
            with self.managed_query() as query:
                query.prepare(f"SELECT ID, WebSideLink FROM AnalVids WHERE WebSideLink LIKE :letter;")
                query.bindValue(":letter",f"%{letter}%")
                query.exec() 
                if query.next():
                    analvids=query.value("WebSideLink").split("\n")[0]
                    analvids_id = query.value("ID") 
            with self.managed_query() as query:
                query.prepare(f"SELECT ID, WebSideLink FROM DDFNetwork WHERE WebSideLink LIKE :letter;")
                query.bindValue(":letter",f"%{letter}%")
                query.exec() 
                if query.next():
                    ddfmodels=query.value("WebSideLink").split("\n")[0]
                    ddfmodels_id = query.value("ID") 
            pornbox = "https://pornbox.com/application/watch-page/"+analvids.split("/")[-2] if analvids else "" 
            if pornworld_id != 0:           
                WebSideLink = "\n".join([item for item in [pornworld, legalporno, analvids, pornbox, ddfmodels] if item])
                with self.managed_query() as query:
                    query.prepare(f"UPDATE PornWorld SET WebSideLink=:WebSideLink, Data18Link=:Data18Link, ThePornDB=:ThePornDB, IAFDLink=:IAFDLink, Movies=:movie WHERE ID=:ID;")
                    query.bindValue(":ID",pornworld_id)
                    query.bindValue(":Data18Link",data18_link)
                    query.bindValue(":ThePornDB",tpdb_link)
                    query.bindValue(":IAFDLink",iafd_link)
                    query.bindValue(":movie",movie)
                    query.bindValue(":WebSideLink",WebSideLink)
                    query.exec()
                self.Main.txtEdit_Clipboard.setText(f"Pornworld Update:\n{WebSideLink}\n-------------------") 
            if legalporno_id != 0: 
                WebSideLink = "\n".join([item for item in [legalporno, pornworld, analvids, pornbox, ddfmodels] if item])
                with self.managed_query() as query:
                    query.prepare(f"UPDATE LegalPorno SET WebSideLink=:WebSideLink, Data18Link=:Data18Link, ThePornDB=:ThePornDB, IAFDLink=:IAFDLink, Movies=:movie WHERE ID=:ID;")
                    query.bindValue(":ID",legalporno_id)
                    query.bindValue(":Data18Link",data18_link)
                    query.bindValue(":ThePornDB",tpdb_link)
                    query.bindValue(":IAFDLink",iafd_link)
                    query.bindValue(":movie",movie)
                    query.bindValue(":WebSideLink",WebSideLink)
                    query.exec()
                self.Main.txtEdit_Clipboard.setText(f"LegalPorno Update:\n{WebSideLink}\n-------------------")            
            if analvids_id != 0: 
                WebSideLink = "\n".join([item for item in [analvids, legalporno, pornworld, pornbox, ddfmodels] if item])
                with self.managed_query() as query:
                    query.prepare(f"UPDATE AnalVids SET WebSideLink=:WebSideLink, Data18Link=:Data18Link, ThePornDB=:ThePornDB, IAFDLink=:IAFDLink, Movies=:movie WHERE ID=:ID;")
                    query.bindValue(":ID",analvids_id)
                    query.bindValue(":Data18Link",data18_link)
                    query.bindValue(":ThePornDB",tpdb_link)
                    query.bindValue(":IAFDLink",iafd_link)
                    query.bindValue(":movie",movie)
                    query.bindValue(":WebSideLink",WebSideLink)
                    query.exec()
                self.Main.txtEdit_Clipboard.setText(f"AnalVids Update:\n{WebSideLink}\n-------------------")
            if ddfmodels_id != 0: 
                WebSideLink = "\n".join([item for item in [ddfmodels, analvids, legalporno, pornworld, pornbox] if item])
                with self.managed_query() as query:
                    query.prepare(f"UPDATE DDFNetwork SET WebSideLink=:WebSideLink, Data18Link=:Data18Link, ThePornDB=:ThePornDB, IAFDLink=:IAFDLink, Movies=:movie WHERE ID=:ID;")
                    query.bindValue(":ID",ddfmodels_id)
                    query.bindValue(":Data18Link",data18_link)
                    query.bindValue(":ThePornDB",tpdb_link)
                    query.bindValue(":IAFDLink",iafd_link)
                    query.bindValue(":movie",movie)
                    query.bindValue(":WebSideLink",WebSideLink)
                    query.exec()
                self.Main.txtEdit_Clipboard.setText(f"DDFNetwork Update:\n{WebSideLink}\n-------------------")
        else:
            self.db_fehler(self.db)
        self.db.close() 
