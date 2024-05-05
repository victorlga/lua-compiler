import re

def filter(code):
    print(code)
    pattern = r'--.*'
    return re.sub(pattern, '', code)
    