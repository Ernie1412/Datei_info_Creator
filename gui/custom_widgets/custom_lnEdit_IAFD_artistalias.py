from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal

class CustomLineEdit_double(QLineEdit):
    doubleClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_click_time = None

    def mousePressEvent(self, event):
        if event.button() ==Qt.MouseButton.LeftButton:
            current_time = event.timestamp()
            if self.last_click_time is not None and current_time - self.last_click_time < 500:  # 500 Millisekunden für den Double-Click
                self.doubleClicked.emit()  # Signal auslösen
            self.last_click_time = current_time
        super().mousePressEvent(event)

if __name__ == '__main__':
    CustomLineEdit_double()