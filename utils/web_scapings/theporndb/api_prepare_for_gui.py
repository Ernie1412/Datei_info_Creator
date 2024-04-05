from datetime import datetime
from utils.web_scapings.theporndb.api_scraper import TPDB_Scraper

class API_Scene:
    @staticmethod
    def get_scene_title(api_data: dict) -> str:
        return api_data['data'].get('title', 'No title')
    
    def get_scene_id(api_data: dict) -> str:
        return api_data['data'].get('id', '/')
    
    def get_scene_description(api_data: dict) -> str:
        return api_data['data'].get('description', '')
    
    def get_site_id(api_data: dict) -> str:
        return f"{api_data['data'].get('site_id', '/')}"
    
    def get_scene_url(api_data: dict) -> str:
        return api_data['data'].get('url', '')
    
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
    
    def get_scene_tags(api_data: dict) -> str:
        tags=api_data['data'].get('tags', '')
        tag_namen=[]
        if tags:            
            for tag in tags:
                tag_namen.append(tag['name'])
        return ";".join(tag_namen) if tag_namen else ''
    
    def get_scene_performers(api_data: dict) -> dict:
        performers=api_data['data'].get('performers', '')
        performers_dict = []
        if performers:
            for performer in performers:
                parent = performer.get('parent')                
                if parent is None:
                    gender = 'Unknown'
                elif parent['extras']['gender'] is None:
                    gender = 'Unknown'  
                else:
                    gender = parent['extras']['gender']

                performer_dict = {
                    'name': performer['name'], 
                    'gender': gender          
                      } 
                performers_dict.append(performer_dict)
        return performers_dict    

    def get_scene_image(api_data: dict) -> str:
        image_url = api_data['data'].get('image', '') 
        if not image_url:
            return None
        return TPDB_Scraper.get_image_data(image_url)
    
class API_Actors:

    @staticmethod 
    def get_actor_data(api_data: dict, key: str) -> str: 
        data_path = api_data['data'] 
        if len(api_data) > 1:
            data_path = api_data['data'][0]  
        elif not data_path:
            return None, 0   
        return data_path.get(key,''), len(api_data['data'])
        
    def get_actor_extras(api_data: dict, key: str) -> str:
        if not api_data.get('data'):
            return ''        
        data_path = api_data['data'][0] if len(api_data)>1 else api_data['data']  
        if data_path['is_parent']:
            return data_path['extras'].get(key)
        else:
            return "Unknown" if key == 'gender' else ''

        
    def get_actor_image(api_data: dict, key:str, counter=None) -> str:                 
        data_path = api_data['data'][0] if len(api_data)>1 else api_data['data']
        if not data_path.get(key, ''):
            return None
        poster_images = data_path[key]
        if counter is None:
            counter = len(poster_images) 
        image_datas = []
        if isinstance(poster_images, str):
            image_datas = TPDB_Scraper.get_image_data(poster_images)
        else:
            for poster in poster_images[:counter]:
                image_url = poster.get('url')
                image_datas.append(TPDB_Scraper.get_image_data(image_url))
        return image_datas, len(poster_images)
                
        