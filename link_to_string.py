import re
import pathlib

class Link_to_String():
    def get_string(self, input_string):  

        input_string = input_string.replace("http://www.firstanalquest.com/videos/","")[:-5]

        # Ersetze alle Bindestriche durch Leerzeichen
        input_string = input_string.replace("-", " ")

        # Präpositionen, die nicht title() bekommen sollen
        prepositions = ["of", "in", "to", "for", "with", "on", "at", "from", "by", "as"]

        # Wende .title() nur auf Wörter an, die keine Präposition sind
        words = []
        for word in input_string.split():
            if word.lower() not in prepositions:
                words.append(word.title())
            else:
                words.append(word)
                
        output_string = " ".join(words)
        print(output_string)

class Renamer():    
    def rename_files(self, folder):
        folder = pathlib.Path(folder)

        for path in folder.glob("*"):
            if path.is_file():
                name = path.name
                new_name = re.sub(r"\[[^]]*\]|-", "", name, 2)
                new_name = new_name.replace("Xxlayna Marie  ", "Xxlayna Marie") 
                new_path = path.with_name(new_name)
                path.rename(new_path)
                print(new_name)

#renamer = Renamer().rename_files("F:\Xxlayna Marie - MegaPACK by SoreForDays")

link="http://www.firstanalquest.com/videos/cute-teen-girl-ally-horny-first-anal-adventure-on-camera-699/"
Link_to_String().get_string(link)


# def cleanup_runtime(text):
#     text = text.replace('\n', '')
#     match = re.search(r'(\d+) min', text)
#     if match:
#         hours = int(match.group(1)) // 60 
#         mins = int(match.group(1)) % 60
#         minutes = f"{hours:02d}:{mins:02d}:00"
#     else:
#         minutes = "00:00:00"            
#     return minutes
# text='\n                        26 min      ...'
# print(cleanup_runtime(text))