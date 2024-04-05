import re
from datetime import datetime
import importlib

def time_format_00_00_00(text: str) -> str:     
    match = re.search(r'(\d+:\d+:\d+|\d+:\d+)', text)
    if match:
        time_parts = match.group(1).split(":")        
        hours = 0
        minutes = 0
        seconds = 0

        if len(time_parts) == 3:
            hours = int(time_parts[0]) 
            minutes = int(time_parts[1])
            seconds = int(time_parts[2])
        elif len(time_parts) == 2:
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])
        time_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        time_formatted = "00:00:00"  
    return time_formatted

def datum_umwandeln(date_str:str, date_format: str) -> str:
    try:
        date_obj = datetime.strptime(date_str, date_format)
    except ValueError:
        return None    
    # Datumsobjekt in das gewünschte Format umwandeln        
    return date_obj.strftime('%Y:%m:%d %H:%M:%S')

def from_classname_to_import(spider_class_name, pipeline=None):
    module_path, class_name = spider_class_name.rsplit('.', 1)
    module = importlib.import_module(module_path)
    klasse = None
    if pipeline:        
        module_path = '.'.join(module_path.split('.')[:-2])+'.pipelines'
        module = importlib.import_module(module_path)       
        class_name = pipeline
    try:
        klasse = getattr(module, class_name)     
    finally:
        return klasse
    
def count_days(start_date, end_date):
    date_format = "%Y.%m.%d"
    a = datetime.strptime(start_date, date_format)
    b = datetime.strptime(end_date, date_format)
    dif = b - a
    return int(dif.days)

def custom_title(text):
  text = re.sub(r"\b(a|an|the|at|by|for|in|of|on|to|up|and|as|but|or|nor)\b", lambda x: x.group(0).lower(), text)
  
  text = re.sub(r"([a-z])'([a-z])", lambda x: x.group(1) + "'" + x.group(2).upper(), text)
  
  return text.title()
