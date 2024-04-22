from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QGroupBox, QPushButton, QSplitter, QLabel, QGridLayout, QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics, QKeyEvent

from gui.custom_widgets.custom_wordwrap_button import QWordWarpButton

class PerformMaskSelection(QDialog):
    send_widget_text = pyqtSignal(QWidget, str)
    def __init__(self, MainWindow, widget_name, parent=None): # von wo es kommt
        super().__init__(parent) 
        self.Main = MainWindow 

        self.widget_name = widget_name
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)        
        self.setupUi() 
        self.show() 
        
    def setupUi(self):        
        self.resize(240, 120)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QSplitter(parent=self)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label = QLabel(parent=self.splitter)
        self.label.setText("")
        self.label.setObjectName("label")
        self.Btn_close = QPushButton(parent=self.splitter)
        self.Btn_close.setMinimumSize(QSize(20, 20))
        self.Btn_close.setMaximumSize(QSize(20, 20))
        self.Btn_close.setAutoFillBackground(False)
        self.Btn_close.setStyleSheet("background-image: url(:/labels/_labels/fenster-schliessen.png);")
        self.Btn_close.setText("")
        self.Btn_close.setFlat(True)
        self.Btn_close.setObjectName("Btn_close")
        self.Btn_close.setToolTip("Fenster schliessen")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        widget_count= self.set_group_button()
        standard_grey = self.Main.palette().color(self.Main.backgroundRole()).name()
        self.setStyleSheet(f""" QDialog {{border: 2px solid black; background-color: {standard_grey};}}""")                
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)        
        self.Btn_close.clicked.connect(self.close)
       

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Escape:
            self.close()
            return            
        super().keyPressEvent(e)
    def set_group_button(self):
        font = QFont("MS Shell Dlg", 8)
        metrics = QFontMetrics(font)        
        self.sources = getattr(self.Main, self.widget_name).toolTip().split("<br>", 1)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)        
        for idx, group_name_and_button_text in enumerate(self.sources):
            group_name, button_text = group_name_and_button_text.split(": ",1)            
            rect = metrics.boundingRect(button_text)  
            rounded_width = max(220, round(rect.width() / 10) * 10)
            rounded_height = max(40, round(rect.height() / 10) * 10 + 10)           
            self.set_button_in_groupbox(group_name, button_text, sizePolicy, idx, rounded_width, rounded_height)
        return len(self.sources)           
    
    def set_button_in_groupbox(self, group_name, button_text, sizePolicy, idx, rect_width, rounded_height):
        groupbox = QGroupBox(parent=self) 
        groupbox.setGeometry(QRect(0, 10, rect_width, rounded_height))       
        groupbox.setMinimumSize(QSize(rect_width, rounded_height))
        groupbox.setMaximumSize(QSize(rect_width, rounded_height))
        groupbox.setTitle(group_name) 
        sizePolicy.setHeightForWidth(groupbox.sizePolicy().hasHeightForWidth())
        setattr(self,f"gBox_selection_{idx}", groupbox)       
        button = QWordWarpButton(parent=groupbox)        
        button.setGeometry(QRect(-8, 12, rect_width+18, rounded_height-2)) 
        button.setSizePolicy(sizePolicy)
        button.setMinimumSize(QSize(rect_width-2, rounded_height-2))
        button.setMaximumSize(QSize(rect_width-2, rounded_height-2))
        button.setStyleSheet(self.button_stylesheet())
        button.setText(button_text)         
        button.clicked.connect(self.selected_button)
        button.setObjectName(f"Btn_selection_{idx}")
        setattr(self,f"Btn_selection_{idx}", button)
        self.gridLayout.addWidget(getattr(self,f"gBox_selection_{idx}"), idx+1, 0, 1, 1)

    def selected_button(self):            
        sender = self.sender()
        
        for idx in range(len(self.sources)):
            if sender.objectName().startswith("Btn_selection_"):                
                widget = getattr(self.Main,self.widget_name)
                widget.setText(sender.text())
                #self.send_widget_text.emit(widget, sender.text())
                break
        
        self.reject()         
       
    def button_stylesheet(self):
        return """QPushButton {background-color: #FFFDD5;}
            QLabel {background-color: transparent;}
            QLabel:hover {border: 2px solid rgb(49, 50, 62);}"""




if __name__ == '__main__':
    PerformMaskSelection(QDialog)