import threading

class ScraperThread(threading.Thread):
    def __init__(self, main_window, feld):
        super().__init__()
        self.main_window = main_window
        self.feld = feld
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():            
            self.main_window.scrap_status(self.feld, "OK")
            # Hier können Sie eine Verzögerung oder weitere Logik einfügen
            

    def stop(self):
        self._stop_event.set()