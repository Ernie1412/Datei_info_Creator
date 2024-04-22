class SocialMediaButtons():

    @staticmethod
    def get_social_media_from_buttons(MainWindow) -> str: 
        social_medias: list = []
        for index in range(10):
            social_media = getattr(MainWindow, f"Btn_performers_socialmedia_{index}").toolTip().replace("Datenbank: ", "")
            if social_media:
                social_medias.append(social_media)
        return social_medias

    
if __name__ == "__main__":
    SocialMediaButtons()