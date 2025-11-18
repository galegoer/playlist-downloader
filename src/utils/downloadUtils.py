import os
import yt_dlp
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3
import urllib.parse

from utils.utils import use_regex
from utils.metaDataUtils import searchAppleMetaData

class QuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(msg)

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

def downloadSong(url, save_path):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            album = info.get('album')
            artist = info.get('artist')
            audio_title = info.get('title')
            print('ALBUM: ', album)
            print('ARTIST: ', artist)
            print('title; ', audio_title)
            
            if (not artist):
                artist = info.get('channel')
            
            # Remove any brackets with (Audio) or (Official Video) etc.
            audio_title = use_regex(audio_title)
            # If artist isn't included add it
            if not artist in audio_title:
                audio_title += ' ' + artist.split(",")[0]
            audio_title, artist, album, track_num, track_total, genre, year = searchAppleMetaData(urllib.parse.quote_plus(audio_title))
            title = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

        # Kind of unnecessary but may be helpful if switching storage methods
        key = audio_title + " - " + artist
        print(key)

        mp3 = MP3(title, ID3=EasyID3)
        mp3['album'] = [album]
        mp3['artist'] = [artist]
        mp3['title'] = [audio_title]
        mp3['date'] = [year]
        mp3['genre'] = [genre]
        mp3['tracknumber'] = [str(track_num)+'/'+str(track_total)]
        mp3.save()
        
        # TODO: take out extra space that may be in title at end
        final_name = title.split(' [')[0]+'.mp3'
        print('FINAL : ' + final_name)

        os.rename(title, save_path+final_name)
        print("DOWNLOADED:", final_name)
        return save_path+final_name
    except Exception as e:
        print("Exception:", e)
        return e