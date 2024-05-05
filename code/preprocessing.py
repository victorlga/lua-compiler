import re
import sys

def filter(code):
    # Write code to stderror
    sys.stderr.write(code)
    pattern = r'--.*'
    return re.sub(pattern, '', code)
    