
import re

image_url ="https://www.babepedia.com/pics/Amalia%20Davis_thumb3.jpg"
cleaned_url = re.sub(r'[/\.jpg%20]', ' ', image_url)

print(cleaned_url)

