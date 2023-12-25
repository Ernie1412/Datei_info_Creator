import requests
from lxml import html
from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import urlencode, urljoin

from config import HEADERS

class playw():

    def block_banner(self, route):        
        #print(f">>{route.request.url}")
        if "revive.iafd.com/www/delivery/asyncspc.php?" in route.request.url:
            print(f"Blocking request to {route.request.url}")
            route.abort()
        else:
            route.continue_()

    def open_url(self, url):
        print(f"{self.open_url.__name__}")
        with sync_playwright() as p:
            page_content=None
            browser = p.chromium.launch(headless=False)
            page = browser.new_page() 
            page.set_extra_http_headers(HEADERS) 
            page.route("**/*", lambda route: self.block_banner(route))                     
            try:                               
                page.goto(url, wait_until="networkidle")                 
            except Exception as e: 
                print(e)
                #infos_webside.fehler_ausgabe_checkweb(e,f"{webdatabase}URL") 
            else:
                if any(keyword in page.content() for keyword in ["The page you requested was removed", "invalid or outdated page"]):
                    self.search_methode=True
                    return

                page_content = html.fromstring(page.content()) 
            finally:
                browser.close()
                return page_content

url='https://www.iafd.com/ramesearch.asp?searchtype=comprehensive&searchstring=Lucy+Shine'

content=playw().open_url(url)
artist_elem=content.xpath("//table[@id='tblFem']/tbody/tr[@class='odd']/td[1]/a")
print(len(artist_elem))