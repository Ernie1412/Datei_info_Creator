from utils.web_scapings.theporndb.helpers.http import Http

import json

from config import EINSTELLUNGEN_JSON_PATH

class TPDB_Scraper:     

    @staticmethod
    def get_tpdb_data(url: str):
        header, key = TPDB_Scraper.get_header()
        if not key:
            return header
        request = Http.get(url, headers=header)
        return request.json()    
    
    def get_image_data(url: str):
        header, key = TPDB_Scraper.get_header()
        if not key:
            return header
        response = Http.get(url, headers=header)
        if response.status_code == 403:
            return '403'
        if response.status_code == 200:
            return response.content
        else:
            return None
        
    
        
    def get_header():
        set = json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes()) 
        api_key = set["theporndb_apikey"]
        if not api_key:
            return {'message': 'key missing'}, False     
        return {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'tpdb-scraper/1.0.0'        }, True 