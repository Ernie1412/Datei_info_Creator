from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import uic

from config import TIMER_DIALOG_UI

### -------------------------------------------------------------------- ###
### --- Timer Dialog für infos die zeitlich wideer verschwinden -------- ###
### -------------------------------------------------------------------- ###
class TimerDialog(QDialog):
    def __init__(self, text, zeit, parent=None):
        super().__init__(parent)        
        uic.loadUi(TIMER_DIALOG_UI,self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # FramelessWindowHint für das Hauptfenster
        self.lbl_timer.setText(f"{zeit}") 
        self.lbl_message.setText(text)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.show()
        self.move(150, 150)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # Timer alle 1 Sekunde

        self.remaining_time = zeit

    def update_timer(self):
        self.remaining_time -= 1
        self.lbl_timer.setText(str(self.remaining_time))

        if self.remaining_time <= 0:
            self.timer.stop()
            self.reject()