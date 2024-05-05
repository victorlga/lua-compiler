import re

def filter(code):
    pattern = r'--.*'
    return re.sub(pattern, '', code)
    