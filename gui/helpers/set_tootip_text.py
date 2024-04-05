class SetTooltipText():
    def __init__(self, MainWindow):
            
        super().__init__() 
        self.Main = MainWindow

    def set_tooltip_text(self, widget: str, info_art: str, tooltip_text: str, source: str) -> None:
        current_tooltip = getattr(self.Main, f"{widget}{info_art}").toolTip()
        tooltip_parts = current_tooltip.split("<br>") if current_tooltip else []
        if not any(source + ": " in item for item in tooltip_parts):            
            tooltip_parts.append(tooltip_text)
        new_tooltip = ("<br>".join(tooltip_parts))
        getattr(self.Main, f"{widget}{info_art}").setToolTip(new_tooltip) 

class SetDatenInMaske():
    def __init__(self, MainWindow):

        super().__init__()
        self.Main = MainWindow
    
    def set_daten_in_maske(self, widget: str, info_art: str, source: str, daten: str, artist=False) -> None:
        if daten is not None:         
            if not artist:
                anzahl=self.Main.datenbank_save(info_art,source,daten)
            if widget in ["lnEdit_DB", "lnEdit_performer_"]:
                getattr(self.Main, f"{widget}{info_art}").setText(daten)
            else:
                getattr(self.Main, f"{widget}{info_art}").setPlainText(daten) 