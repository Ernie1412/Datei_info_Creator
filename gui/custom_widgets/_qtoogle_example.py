from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QFont

import sys

from qtoogle import QToggle

class QToggleExample(QWidget):
    def __init__(self, parent=None):
        super(QToggleExample,self).__init__(parent)
    
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.checkbox0 = QToggle()
        self.checkbox0.setFixedHeight(20)
        self.layout.addWidget(self.checkbox0)

        self.checkbox1 = QToggle()
        self.checkbox1.setText('Checkbox 1 - Disabled')
        self.checkbox1.setEnabled(False)
        self.layout.addWidget(self.checkbox1)

        self.checkbox2 = QToggle()
        self.checkbox2.setText('Checkbox 2 - Checked, custom height, animation duration, colors and font')
        self.checkbox2.setFixedHeight(24)
        self.checkbox2.setFont(QFont('Segoe Print', 10))
        self.checkbox2.setStyleSheet("QToggle{"
                                "qproperty-bg_color:#FAA;"
                                "qproperty-circle_color:#DDF;"
                                "qproperty-active_color:#AAF;"
                                "qproperty-disabled_color:#777;"
                                "qproperty-text_color:#A0F;}")
        self.checkbox2.setDuration(2000)
        self.checkbox2.setChecked(True)
        self.layout.addWidget(self.checkbox2)
        
        # Abschluss
if __name__ == '__main__':
    app, MainWindow =(QApplication(sys.argv), QToggleExample())  
    
    MainWindow.show()   
    sys.exit(app.exec())