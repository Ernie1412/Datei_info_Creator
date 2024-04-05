from utils.database_settings.database_for_settings import Webside_Settings
from utils.helpers.umwandeln import from_classname_to_import

class ScapyPipelineSettings():
    def __init__(self, MainWindow):
            
        super().__init__() 
        self.Main = MainWindow

    def pipeline_add_link(self, url):
        links = url
        baselink = "/".join(url.split("/")[:3])+"/"
        db_webside_settings = Webside_Settings(MainWindow=self.Main)      
        errorview, spider_class_name = db_webside_settings.from_link_to_spider(baselink)
        errorview, studio = db_webside_settings.from_link_to_studio(baselink)       
        if not errorview:
            spider_class_pipeline = from_classname_to_import(spider_class_name, pipeline=f"{studio}Settings") ## import der Klasse "BangBrosAddDistri"
            if spider_class_pipeline: 
                # Rufe die Funktion auf                
                instance = spider_class_pipeline()
                links = instance.add_link(url)
        return links

    def pipeline_movie_distr(self, url, jahr):
        distr: str=""        
        baselink = "/".join(url.split("/")[:3])+"/"        
        db_webside_settings = Webside_Settings(MainWindow=self.Main)      
        errorview, spider_class_name = db_webside_settings.from_link_to_spider(baselink) 
        errorview, studio = db_webside_settings.from_link_to_studio(baselink)            
        if errorview:
            distr = url
        elif spider_class_name:       
            spider_class_pipeline = from_classname_to_import(spider_class_name, pipeline=f"{studio}Settings") ## import der Klasse "Pipeline"
            if spider_class_pipeline: 
                # Rufe die Funktion auf
                instance = spider_class_pipeline()
                distr = instance.movie_distr(spider_class_name, jahr)  
        return distr.split("\n") 