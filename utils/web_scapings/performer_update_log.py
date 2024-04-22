from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

import json

from config import PROJECT_PATH, UPDATE_PERFORMER_LOG_UI

class PerformerUpdateLogger(QDialog):
    def __init__(self, parent=None):
        super(PerformerUpdateLogger, self).__init__(parent)        
    
    @classmethod
    def save_performer_update_log(cls, performer_id, performer_name, update_datas):
        diff_dict = {}
        update = {}
        for key, value in update_datas:
            diff_dict[key] = diff_dict.get(key, ()) + (value,)
        for key, (val1, val2) in diff_dict.items():
            update[key]=f" {val1} != {val2}"

        filename = f"{performer_id}_{performer_name}.log"
        with open(PROJECT_PATH / "log_files" / "performer_update" / filename, 'w') as f:
            json.dump(update, f)
        return filename
   
    def load_performer_update_log(self, filename):        
        with open(PROJECT_PATH / "log_files" / "performer_update" / filename, 'r') as f:
            return json.load(f)
        
    def show_performer_update_log(self, filename):
        log = self.load_performer_update_log(filename)
        formatted_json = json.dumps(log, indent=4).replace("{", "").replace("}", "")
        uic.loadUi(UPDATE_PERFORMER_LOG_UI, self)
        self.setWindowTitle(f"Performer Update Log: {filename}")
        self.lbl_update_performer_log.setText(formatted_json)
        self.exec()
        self.show()

if __name__ == "__main__":
    PerformerUpdateLogger(QDialog)