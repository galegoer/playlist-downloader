
global debugger
debugger = open("debugger.txt", "a")

class QuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): debugger.write(msg+"\n")

RETRY = 3
DOWNLOAD_LINK = "https://youtube.com/watch?v="
YDL_OPTS = {
    'logger': QuietLogger(),
    'quiet': True,
    'no_warnings': True,
    'format': 'bestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',},
    ],
}
IGNORE_TERMS = [
    "Audio",
    "Vizualizer",
    "Lyrics",
    "Official"
]
START_NUM = 1
SAVE_PATH = "Downloads/"