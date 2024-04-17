from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize

from datetime import datetime
import json

from config import EINSTELLUNGEN_JSON_PATH

def date_formarted(date: str) -> str:
    if not date:
        return "",""
    date = datetime.strptime(date, "%Y-%m-%d").date()
    format1 = date.strftime("%d %b., %Y") # Format 1: 10 Jan., 1992      
    format2 = date.strftime("%d.%m.%Y") # Format 2: 10.01.1992 
    return format1, format2

def get_image_counter():
    set = json.loads(EINSTELLUNGEN_JSON_PATH.read_bytes()) 
    image_counter = set["tpdb_image_counter"]
    return image_counter

def check_avaible_bio_websites(Main):
    widget = Main.get_bio_websites(widget=True)[1]
    icon = QIcon()
    icon.addPixmap(QPixmap(f":/Buttons/_buttons/performer_biosites/{widget}.png"), QIcon.Mode.Normal, QIcon.State.Off)
    bio_button = getattr(Main, f"Btn_performer_in_{widget}")
    bio_button.setIcon(icon)
    bio_button.setIconSize(QSize(50, 25))
    Main.Btn_DBArtist_Update.setEnabled(True)