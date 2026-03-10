import re
import time
from urllib.request import Request, urlopen, HTTPError
from urllib.parse import urlparse

QUERY_TEMPLATE = "https://itunes.apple.com/search?term=%s&media=music&entity=album"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
THROTTLED_HTTP_CODES = [403, 429]
IGNORE_TERMS = [
    "Audio",
    "Vizualizer",
    "Lyrics",
    "Official",
    "Remastered",
    "Remaster",
    "Deluxe Edition",
]

def use_regex(input_text):
    # return re.sub(r'[\[\{\(](.*?' + '|'.join(map(re.escape, IGNORE_TERMS)) + r'.*?)[\}\)\]]', '', input_text, flags=re.IGNORECASE)
    return re.sub(r'[\[\{\(](.*?)[\}\)\]]', '', input_text, flags=re.IGNORECASE)

def _urlopen_safe(url):
    for i in range(3):
        try:
            q = Request(url)
            q.add_header("User-Agent", USER_AGENT)
            response = urlopen(q)
            return response.read()
        except HTTPError as e:
            if e.code in THROTTLED_HTTP_CODES:
                # we've been throttled, time to sleep
                domain = urlparse(url).netloc
                print(f"WARNING: Request limit exceeded from {domain}, trying again in {self.throttle} seconds...")
                time.sleep(10)
            else:
                raise e