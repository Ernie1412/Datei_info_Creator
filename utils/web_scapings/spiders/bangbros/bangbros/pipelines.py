# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime


class BangBrosPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        date_format = self.datum_umwandeln(adapter.get("release_date"),"%B %d, %Y") # z.B. November 20, 2023
        adapter["release_date"] = date_format
        if adapter["url"].startswith("https://bangbros.com/"):
            bangbrosnetwork = adapter["url"].replace("https://bangbros.com/","https://www.bangbrosnetwork.com/").replace("/video/","/videos/")
            adapter["url"] = adapter["url"] + "\n" + bangbrosnetwork
        if adapter["url"].startswith("https://www.bangbrosnetwork.com/"):
            bangbros = adapter["url"].replace("https://www.bangbrosnetwork.com/","https://bangbros.com/").replace("/videos/","/video/")
            adapter["url"] = adapter["url"] + "\n" + bangbros
        return item

    
    def datum_umwandeln(self,date_str:str, date_format: str) -> str:
        try:
            date_obj = datetime.strptime(date_str, date_format)
        except ValueError:
            return None    
        # Datumsobjekt in das gewünschte Format umwandeln        
        return date_obj.strftime('%Y.%m.%d %H:%M:%S')
