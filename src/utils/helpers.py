import re
from config.settings import IGNORE_TERMS

def use_regex(input_text):
    return re.sub(r'[\[\{\(](.*?' + '|'.join(map(re.escape, IGNORE_TERMS)) + r'.*?)[\}\)\]]', '', input_text, flags=re.IGNORECASE)