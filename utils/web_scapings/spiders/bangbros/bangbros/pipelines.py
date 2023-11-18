# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from utils.umwandeln import datum_umwandeln
from utils.database_settings.database_for_scraping import DB_Webside

class BangBrosPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        date_format = datum_umwandeln(adapter.get("release_date"),"%B %d, %Y") # z.B. November 20, 2023        
        adapter["release_date"] = date_format

        if adapter["url"].startswith("https://bangbros.com/"):
            bangbrosnetwork = adapter["url"].replace("https://bangbros.com/","https://www.bangbrosnetwork.com/").replace("/video/","/videos/")
            adapter["url"] = adapter["url"] + "\n" + bangbrosnetwork
        if adapter["url"].startswith("https://www.bangbrosnetwork.com/"):
            bangbros = adapter["url"].replace("https://www.bangbrosnetwork.com/","https://bangbros.com/").replace("/videos/","/video/")
            adapter["url"] = adapter["url"] + "\n" + bangbros

        return item  
    

class MyDatabasePipeline:
    def __init__(self):
        self.db_connector = DB_Webside()  # Passe dies entsprechend an

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        daten_satz={}

        studio = 'BangBros'
        webside_link = adapter.get('url')
        daten_satz["Titel"] = adapter.get('title')
        daten_satz["WebSideLink"] = adapter.get('url')
        daten_satz["Data18Link"] = None
        daten_satz["IAFDLink"] = None
        daten_satz["ReleaseDate"] = adapter.get('release_date')
        daten_satz["Dauer"] = None
        daten_satz["Performers"] = adapter.get('performers')
        daten_satz["Alias"] = None
        daten_satz["Action"] = None
        daten_satz["Synopsis"] = adapter.get('synopsis')
        daten_satz["Tags"] = adapter.get('tags')
        daten_satz["Serie"] = adapter.get('sub_side')
        daten_satz["SceneCode"] = None
        
        errorview, anzahl = self.db_connector.update_videodaten_in_db(studio, webside_link, daten_satz)
        if errorview == "Link nicht gefunden !":
            self.db_connector.add_neue_videodaten_in_db(studio, webside_link, daten_satz)       
            

        return item