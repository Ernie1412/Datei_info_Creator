from PyQt6.QtWidgets import QLineEdit, QMainWindow, QPushButton
from PyQt6.QtCore import Qt

class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = [""]
        self.history_index = -1

    def keyPressEvent(self, event):        
        if event.key() == Qt.Key.Key_Up:
            self.showPreviousHistory()
        elif event.key() == Qt.Key.Key_Down:
            self.showNextHistory()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        # if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
        #     self.onEnterPressed()

        if event.key() not in [Qt.Key.Key_Up, Qt.Key.Key_Down]:
            super().keyReleaseEvent(event)

    def showPreviousHistory(self):        
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.setText(self.history[self.history_index])

    def showNextHistory(self):               
        if self.history_index > 0:
            self.history_index -= 1
            self.setText(self.history[self.history_index])
        elif self.history_index == 0:
            self.history_index = -1
            self.clear()

    def addToHistory(self, text):
        current_text = self.text().strip()
        if current_text:
            self.history.insert(self.history_index, current_text)
            self.history = list(set(self.history))
            self.history_index = len(self.history)

    
    def findMainWindow(self, widget):
    # Durch die Hierarchie der Elternobjekte gehen, bis das QMainWindow gefunden wird
        while widget is not None:
            if isinstance(widget, QMainWindow):
                return widget
            widget = widget.parent()

        return None

