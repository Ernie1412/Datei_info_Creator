from pathlib import Path
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import SessionNotCreatedException

from collections import namedtuple

WebDriverResult = namedtuple('WebDriverResult', ['driver', 'status_bar'])

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#HEADERS = {"user_agent":"Mozilla\/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko\/20100101 Firefox\/112.0"}

EXIFTOOLPFAD=r'E:\Python\ExifTool\exiftool'


### JSON dateien ####
JSON_PATH = Path(__file__).absolute().parent / 'jsons/'
WEBSITES_JSON_PATH = Path(__file__).absolute().parent / "jsons/websides.json"
EINSTELLUNGEN_JSON_PATH = Path(__file__).absolute().parent / "jsons/einstellung.json"
LINKS_JSON_PATH = Path(__file__).absolute().parent / "jsons/links.json"
BUTTONSNAMES_JSON_PATH = Path(__file__).absolute().parent / "jsons/button_names.json"
PROCESS_JSON_PATH = Path(__file__).absolute().parent / "jsons/process.json"
MEDIA_JSON_PATH = Path(__file__).absolute().parent / "jsons/media.json"
DATENBANK_JSON_PATH = Path(__file__).absolute().parent / "jsons/datenbank.json"
DB_RECORD_JSON = Path(__file__).absolute().parent / 'jsons/db_record.json'
WEBINFOS_JSON_PATH = Path(__file__).absolute().parent / 'jsons/webinfos.json'

DB_PATH = Path(__file__).absolute().parent / '__DB/'
PROJECT_PATH = Path(__file__).absolute().parent
ICON_PATH = PROJECT_PATH / 'grafics/_buttons/'

SPIDER_MONITOR_UI = Path(__file__).absolute().parent / "gui/uic_imports/spidermonitor.ui"
EINSTELLUNG_UI = Path(__file__).absolute().parent / "gui/uic_imports/einstellungen.ui"
TIMER_DIALOG_UI = Path(__file__).absolute().parent / "gui/uic_imports/msg_box_timer.ui"
LOESCH_DIALOG_UI = Path(__file__).absolute().parent / "gui/uic_imports/loeschen.ui"
RENAME_DIALOG_UI = Path(__file__).absolute().parent / "gui/uic_imports/rename.ui" 
DATEI_AUSWAHL_UI = Path(__file__).absolute().parent / "gui/uic_imports/datei_auswahl.ui"
MAIN_UI = Path(__file__).absolute().parent / "gui/uic_imports/datei_info_creator.ui"
BUTTONS_WEBSIDES_UI = Path(__file__).absolute().parent / "gui/uic_imports/button_websides.ui"
TRANSFER_UI = Path(__file__).absolute().parent / "gui/uic_imports/transfer.ui"
ADD_PERFORMER_UI = Path(__file__).absolute().parent / "gui/uic_imports/dialog_performer_add.ui"
ID_MERGE_PERFORMER_UI = Path(__file__).absolute().parent / "gui/uic_imports/dialog_performer_id_merge.ui"
ADD_NEW_PERFORMER_UI = Path(__file__).absolute().parent / "gui/uic_imports/dialog_performer_add_from_link.ui"
ADD_NAMESLINK_PERFORMER_UI = Path(__file__).absolute().parent / "gui/uic_imports/dialog_performer_add_nameslink.ui"
URL_INPUT_DIALOG_UI = Path(__file__).absolute().parent / "gui/uic_imports/url_input_dialog.ui"
GENDER_AUSWAHL_UI = Path(__file__).absolute().parent / "gui/uic_imports/dlg_gender_auswahl.ui"
NATIONS_AUSWAHL_UI = Path(__file__).absolute().parent / "gui/uic_imports/dlg_nations_auswahl.ui"
SOCIAL_MEDIA_AUSWAHL_UI = Path(__file__).absolute().parent / "gui/uic_imports/dlg_social_media_auswahl.ui"
SOCIAL_MEDIA_LINK_UI = Path(__file__).absolute().parent / "gui/uic_imports/dialog_set_socialmedia_link.ui"
PERFORM_MASK_SELECTION_UI = Path(__file__).absolute().parent / "gui/uic_imports/dialog_auswahl_buttons.ui"
SRACPE_ACTOR_INFOS_UI = Path(__file__).absolute().parent / "gui/uic_imports/dialog_gui/dialog_scrape_actor_infos.ui"

### ------------------- Pfade zu den Datenbanken --------------------- ###
SETTINGS_DB_PATH = str(Path(__file__).absolute().parent / '__DB/Webside_Settings.db')
SIDE_DATAS_DB_PATH = str(Path(__file__).absolute().parent / '__DB/WebSide-Downloads.db')
PERFORMER_DB_PATH = str(Path(__file__).absolute().parent / '__DB/DBDarsteller.db')



def selenium_browser_check() -> WebDriverResult:
    status_bar: str=None
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--incognito")
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    try:
        driver_path = ChromeDriverManager().install()
    except (SessionNotCreatedException, ValueError) as e:
        status_bar=f"Fehler beim ChromeUpdate: {e}"            
    driver = webdriver.Chrome(options=options)
    return WebDriverResult(driver=driver, status_bar=status_bar)