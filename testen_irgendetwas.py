import re
value = '108 '
value = re.findall(r'\d+', value)[-1]
print(value)