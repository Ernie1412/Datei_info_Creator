from datetime import datetime
from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper

class API_Scene:

    @staticmethod
    def get_scene_data(api_data: dict, key: str) -> str:
        result = api_data['data'].get(key, '')
        return result if result else "" 
            
        
    
    def get_scene_performers(api_data: dict) -> str:
        if api_data['data'].get('performers'):
            performers = api_data['data']['performers']
            performers_list = []
            for performer in performers:
                performer_name = performer.get('name', None)
                alias = None 
                if performer_name.get('parent'):
                    performer_name, alias = performer_name['parent']['name'], performer_name    
                performer_dict = {performer_name: alias}                                
                performers_list.append(performer_dict)
            return performers_list
        else:
            return None       
    
    def get_scene_site(api_data: dict) -> str:
        if api_data['data'].get('site'):
            site = api_data['data']['site']
            site_name = site.get('name', '')
            site_network = site.get('network', '')
            return site_name, site_network if site_network else site_name                        
    
    def get_scene_tags(api_data: dict) -> str:
        if api_data['data'].get('tags'):
            tags_name = api_data['data']['tags']
            tags = []
            for tag_name in tags_name:
                tags.append(tag_name['name'])            
            return ";".join(tags)
        else:
            return None
    
    def get_scene_releasedate(api_data: dict) -> str:
        date = api_data['data'].get('date', '')
        if date:
            date_obj = datetime.strptime(date, "%Y-%m-%d")            
            return date_obj.strftime("%Y:%m:%d %H:%M:%S")
        else:
            return ''        
    
    def get_scene_duration(api_data: dict) -> str:
        seconds = api_data['data'].get('duration', '')
        if seconds:
            datetime_obj = datetime.fromtimestamp(seconds)
            return datetime_obj.strftime("%H:%M:%S")
        else:
            return ''

    def get_scene_image(api_data: dict) -> str:
        image_url = api_data['data'].get('image', '') 
        if not image_url:
            return None
        return TPDB_Scraper.get_image_data(image_url)
    
class API_Actors:

    @staticmethod 
    def get_actor_data(api_data: dict, key: str) -> str: 
        data_path = api_data.get('data') 
        if len(api_data) > 1:
            data_path = api_data['data'][0]  
        elif not data_path:
            return None, 0   
        return data_path.get(key,''), len(api_data['data'])
        
    def get_actor_extras(api_data: dict, key: str) -> str:
        if not api_data.get('data'):
            return ''        
        data_path = api_data['data'][0] if len(api_data)>1 else api_data['data']  
        if data_path.get('is_parent'):
            return data_path['extras'].get(key)
        else:
            return "Unknown" if key == 'gender' else ''

        
    def get_actor_image(api_data: dict, key:str, no_image, counter=None) -> str:                 
        data_path = api_data['data'][0] if len(api_data)>1 else api_data['data']
        if not data_path.get(key, ''):
            return None, 0
        poster_images = data_path[key]
        if counter is None:
            counter = len(poster_images) 
        image_datas = []
        if isinstance(poster_images, str):
            image_datas = TPDB_Scraper.get_image_data(poster_images)
        else:
            for poster in poster_images:
                image_url = poster.get('url')
                if no_image==True:
                    image_data = None
                else:
                    image_data = TPDB_Scraper.get_image_data(image_url)                     
                if image_data:
                    image_datas.append({image_url: image_data})
                if len(image_datas) == counter:
                    break
        return image_datas, len(poster_images)
                
        