from tpdb.helpers.http import Http


TPDB_API_KEY = 'XkNlfI63KFqSp1sTHwQbcLbrU1vsfQ6mpmk86ejgd187d4dc'

class TPDB_Scraper:
    def __init__(self, url: str): 
        headers = {
            'Authorization': f'Bearer {TPDB_API_KEY}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'tpdb-scraper/1.0.0'
        }
    def get_tpdb_data(self, url: str):
        self.request = Http.get(url, headers=self.headers)
        return self.request.json()

