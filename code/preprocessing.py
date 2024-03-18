import re

class PreProcessing:

    @staticmethod
    def filter(code):
        pattern = r'--.*'
        return re.sub(pattern, '', code)
    