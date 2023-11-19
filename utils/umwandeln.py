import re
from datetime import datetime
import sys
import importlib

def time_format_00_00_00(text: str) -> str:
    hh_mm_ss = None 
    match = re.search(r'(\d+:\d+:\d+|\d+:\d+)', text)
    if match:
        duration = f"00:{match.group(1)}"  # Extrahierte Zeit
        # Falls erforderlich, in das Format "00:00:00" konvertieren
        hh_mm = list(reversed(duration.split(":")))   
        hh_mm_ss = f"{int(hh_mm[2]):02}:{int(hh_mm[1]):02}:{int(hh_mm[0]):02}"
    else:
        hh_mm_ss = None
    return hh_mm_ss

def datum_umwandeln(date_str:str, date_format: str) -> str:
    try:
        date_obj = datetime.strptime(date_str, date_format)
    except ValueError:
        return None    
    # Datumsobjekt in das gewünschte Format umwandeln        
    return date_obj.strftime('%Y.%m.%d %H:%M:%S')

def from_classname_to_import(spider_class_name, pipeline=None):
    module_path, class_name = spider_class_name.rsplit('.', 1)
    module = importlib.import_module(module_path)
    klasse = None
    class_name = pipeline if pipeline else spider_class_name 
    try:
        klasse = getattr(module, class_name)
    except AttributeError:
        klasse = None 
    return klasse