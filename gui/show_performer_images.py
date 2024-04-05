
from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QRect
from pathlib import Path
import pyperclip

from utils.database_settings.database_for_darsteller import DB_Darsteller
from config import PROJECT_PATH

class ShowPerformerImages(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.Main = parent        
        self.current_image_index: int = 0
        self.images: list=[]
        self.links: list=[]         
        self.name: str=None 
        self.connections()

    def connections(self):
        self.Main.Btn_copy_clipboard.clicked.connect(lambda: pyperclip.copy(self.Main.lbl_link_from_image.text()))

    def show_performer_picture(self):
        self.Main.stacked_image_infos.setCurrentWidget(self.Main.perfomer_image)
        self.current_image_index = 0
        errorview=None
        if self.Main.tblWdg_performer_links.hasFocus():
            self.get_performer_image_from_maske()           
        else: 
            errorview=self.get_performer_image_from_db()
        if not errorview:  
            if self.images:                                          
                self.show_performers_picture_in_label()
                if self.Main.tblWdg_performer_links.hasFocus() or self.Main.Btn_performer_next.hasFocus() or self.Main.Btn_performer_prev.hasFocus():
                    widget="Btn_performer"                     
                else:               
                    widget="Btn"
                getattr(self.Main, f"{widget}_next").setEnabled(True)
                getattr(self.Main, f"{widget}_prev").setEnabled(True)
            else:                
                self.Main.lbl_LinkBild.clear()
                self.Main.lbl_link_from_image.clear()
                self.Main.Btn_next.setEnabled(False)
                self.Main.Btn_prev.setEnabled(False)

    def get_performer_image_from_db(self):
        name = self.Main.cBox_performers.currentText()                
        db_darsteller = DB_Darsteller(MainWindow=self.Main)
        errorview, self.images, self.links = db_darsteller.get_performers_picture(name)
        return errorview
    
    def get_performer_image_from_maske(self):        
        self.images: list=[]
        self.links: list=[]
        for zeile in range(self.Main.tblWdg_performer_links.rowCount()):
            image_pfad = self.Main.tblWdg_performer_links.item(zeile, 2).text() if self.Main.tblWdg_performer_links.item(zeile, 2) else ""
            self.images.append(image_pfad)
            self.links.append(self.Main.tblWdg_performer_links.item(zeile, 1).text()) 
        self.current_image_index=self.Main.tblWdg_performer_links.currentRow()         

    def show_performers_picture_in_label(self):                      
        pixmap = QPixmap(str(Path(PROJECT_PATH, self.images[self.current_image_index]))) 
        error: str = ""
        aspect_ratio: int=0
        try:               
            aspect_ratio = pixmap.width() / pixmap.height()
        except ZeroDivisionError as e:
            error = f"(Kein Bild gespeichert)"                  
            pixmap = QPixmap(":/labels/_labels/kein-bild.jpg")
            aspect_ratio = pixmap.width() / pixmap.height()
        label_height = 280
        label_width = int(label_height * aspect_ratio)
        if self.Main.tblWdg_performer_links.hasFocus() or self.Main.Btn_performer_next.hasFocus() or self.Main.Btn_performer_prev.hasFocus():
            self.Main.Btn_performer_next.setGeometry(label_width+20,140,20,50)
            self.Main.lbl_link_image_from_db.setGeometry(20, 20, label_width, label_height)         
            self.Main.lbl_link_image_from_db.setPixmap(pixmap)
            img=self.images[self.current_image_index] 
            img=img[img.find("/[")+2:img.find("]-")]  
            self.Main.lbl_performer_link.setText(self.links[self.current_image_index])        
            self.Main.lbl_link_image_from_db.setToolTip(f"{img}: {self.images[self.current_image_index]} Bilder {error}")
        else:
            self.show_image_in_ui(pixmap, label_width, label_height, error)

    def show_image_in_ui(self,pixmap, label_width, label_height, error):
        self.Main.lbl_LinkBild.setGeometry(120, 350, label_width, label_height)         
        self.Main.lbl_LinkBild.setPixmap(pixmap)
        self.Main.lbl_link_from_image.setText(self.links[self.current_image_index])
        self.Main.lbl_LinkBild.setToolTip(f"Position: {self.current_image_index+1} von {len(self.images)} Bilder {error}")


    def show_next_picture_in_label(self):        
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            return self.show_performers_picture_in_label()

    def show_previous_picture_in_label(self):               
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            return self.show_performers_picture_in_label()  