import re

@staticmethod
def sanitize_string(string):
    return re.sub(r"[\t\n\r]+", " ", string)