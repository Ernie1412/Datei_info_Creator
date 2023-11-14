from PyQt6.QtCore import QThread, pyqtSignal
from threading import Event, Thread
import json
import shutil
from pathlib import Path
import subprocess
from time import monotonic

from config import PROCESS_JSON_PATH

class ExifSaveThread(QThread):
    Exif_Progress = pyqtSignal(int, float, int, int) # Signal für Fortschrittsanzeige und Geschwindigkeitsanzeige
    finished = pyqtSignal(float, int)

    def __init__(self, source_path: str=None, command: str=None, parent: str=None) -> None: 
        super().__init__(parent)                      
        self.source_path: str = source_path
        self.command: str = command
        self.avg_speed: int = 0        
        self.elapsed_time: int = 0
        self.stop_event: Event = Event()
        self.process: str = None  # Prozess-Instanz hinzugefügt

    def run(self):
        process_output: dict = json.loads(PROCESS_JSON_PATH.read_bytes())
        
        if shutil.disk_usage(self.source_path).free < Path(self.source_path).stat().st_size:
            stderr: str = "Nicht genügend Speicher zur Verfügung"
            stdout: str = "0 image files updated\r\n    1 files weren't updated due to errors"
            self.is_running: bool = False
        else:
            self.is_running: bool = True
            try:
                self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as error:
                stderr: str = str(error)
                self.is_running: bool = False
            else:
                Thread(target=self.check_exif_progress).start()
                
            self.process.wait()  # Warte auf das Beenden des Prozesses

        # Verarbeite die Standardausgabe und den Standardfehler hier
        if self.process:
            stdout, stderr = self.process.communicate()
            stderr: str = stderr.decode('utf-8')
            stdout: str = stdout.decode('utf-8').strip()
            self.is_running: bool = False

        if stderr == "":            
            process_output["stdout"]: str = stdout
        else:
            process_output["stderr"]: str = stderr
            process_output["stdout"]: str = stdout

        json.dump(process_output, open(PROCESS_JSON_PATH, 'w'), indent=4, sort_keys=True)
        self.finished.emit(self.avg_speed, int(self.elapsed_time))

    def check_exif_progress(self):
        buffer_size: int = 1024 * 1024
        exif_size: int = 0
        start_time: float = monotonic()
        progress: int = 0

        while not self.stop_event.is_set():
            tmp_file = Path(f"{self.source_path}_exiftool_tmp")
            if tmp_file.exists():
                exif_size = Path(tmp_file).stat().st_size
                self.elapsed_time = monotonic() - start_time
                self.avg_speed = exif_size / buffer_size / self.elapsed_time
                if self.avg_speed < 0.01:
                    self.avg_speed = 0.01
                remaining_time = int(Path(self.source_path).stat().st_size / buffer_size / self.avg_speed - self.elapsed_time)
                progress = int(exif_size / Path(self.source_path).stat().st_size * 100)
                self.Exif_Progress.emit(progress, self.avg_speed, remaining_time, int(self.elapsed_time))
                if progress == 100:
                    self.is_running = False
                    break
            elif progress > 0:
                progress = 100
                self.is_running = False
                break

### -------------------------------------------------------------------- ###
### --------------------- Transfer im richtigen Ordner ----------------- ###
### -------------------------------------------------------------------- ###
class FileTransferThread(QThread):
    updateProgress = pyqtSignal(int, float, int) # Signal für Fortschrittsanzeige und Geschwindigkeitsanzeige
    transferFinished = pyqtSignal()
    abort_signal = pyqtSignal(float, int)# Signal für Geschwindigkeitsanzeige 

    def __init__(self, source_path: str=None, target_path: str=None, parent: str=None):
        super().__init__(parent)
        self.source_path: str = source_path
        self.target_path: str = target_path
        self.stop_event: Event = Event()  # Event-Objekt für das Beenden des Threads
        self.abort: bool = False  # Initialisiere self.abort

    def run(self):
        buffer_size: int = 1024 * 1024  # 1MB buffer
        bytes_transferred: int = 0
        start_time: monotonic = monotonic()
        
        with open(self.source_path, 'rb') as source_file, open(self.target_path, 'wb') as target_file:
            while not self.stop_event.is_set():  # Überprüfung des Event-Objekts
                buffer = source_file.read(buffer_size)
                if not buffer:
                    break
                target_file.write(buffer)
                bytes_transferred += len(buffer)
                elapsed_time = monotonic() - start_time
                avg_speed = bytes_transferred / buffer_size / elapsed_time
                remaining_time = int(Path(self.source_path).stat().st_size / buffer_size / avg_speed - elapsed_time)
                progress = bytes_transferred / Path(self.source_path).stat().st_size * 100
                self.updateProgress.emit(int(progress), avg_speed, remaining_time)
                if self.abort:
                    self.abort_signal.emit(avg_speed, remaining_time)
                    return  
                              
        shutil.copystat(self.source_path, self.target_path)        
        self.transferFinished.emit()                
         
    
    def stop(self):
        self.abort = True  # Signalisiere den Abbruch des Threads
        self.stop_event.set()  # Setze das Event-Objekt, um den Thread zu beenden