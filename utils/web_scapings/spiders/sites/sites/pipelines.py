# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from utils.helpers.umwandeln import datum_umwandeln
from utils.database_settings.database_for_scrapings import ScrapingData
from datetime import datetime

class BangBrosPipeline:
    def process_item(self, item, spider):        
        adapter = ItemAdapter(item) 
        if adapter.get("release_date"):       
            date_format = datum_umwandeln(adapter.get("release_date"),"%B %d, %Y") # z.B. November 20, 2023        
            adapter["release_date"] = date_format

        if adapter.get("url"):
            if adapter["url"].startswith("https://bangbros.com/"):
                bangbrosnetwork = adapter["url"].replace("https://bangbros.com/","https://www.bangbrosnetwork.com/").replace("/video/","/videos/")
                adapter["url"] = adapter["url"] + "\n" + bangbrosnetwork
            if adapter["url"].startswith("https://www.bangbrosnetwork.com/"):
                bangbros = adapter["url"].replace("https://www.bangbrosnetwork.com/","https://bangbros.com/").replace("/videos/","/video/")
                adapter["url"] = adapter["url"] + "\n" + bangbros

        return item  
    

class MyDatabasePipeline:
    def __init__(self):
        self.db_connector = ScrapingData()  # Passe dies entsprechend an

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        daten_satz={}

        studio = adapter.get('studio')
        webside_link = adapter.get('url')
        daten_satz["Titel"] = adapter.get('title')        
        daten_satz["Data18Link"] = None
        daten_satz["IAFDLink"] = None
        daten_satz["ThePornDB"] = None
        daten_satz["ReleaseDate"] = adapter.get('release_date')
        daten_satz["Dauer"] = adapter.get('during')
        daten_satz["Performers"] = adapter.get('performers')
        daten_satz["Alias"] = None
        daten_satz["Action"] = None
        daten_satz["Synopsis"] = adapter.get('synopsis')
        daten_satz["Tags"] = adapter.get('tags')
        daten_satz["Serie"] = adapter.get('sub_site')
        daten_satz["SceneCode"] = adapter.get('scene_code')
        daten_satz["Regie"] = adapter.get('director')
        daten_satz["ProDate"] = None
        daten_satz["SceneCode"] = adapter.get('scene_code')
        daten_satz["Movies"] = None        
        
        errview, id = self.db_connector.get_id_from_websidelink(webside_link, studio)        
        if id and not errview:
            daten_satz["ID"] = id
            self.db_connector.update_videodaten_in_db(studio, webside_link, daten_satz)
        else:
            errview, isneu = self.db_connector.add_neue_videodaten_in_db(studio, webside_link, daten_satz)
                
        return item
    
class BangBrosSettings:

    @classmethod
    def add_link(cls, link):
        if link.startswith("https://bangbros.com/"):
            bangbrosnetwork = link.replace("https://bangbros.com/","https://www.bangbrosnetwork.com/").replace("/video/","/videos/")
            links = link + "\n" + bangbrosnetwork
        if link.startswith("https://www.bangbrosnetwork.com/"):
            bangbros = link.replace("https://www.bangbrosnetwork.com/","https://bangbros.com/").replace("/videos/","/video/")
            links = link + "\n" + bangbros
        return links 
    
    @classmethod
    def movie_distr(cls, studio, jahr):
        return "BangProductions" if jahr < 2017 else "GirlFriendsFilms"   
