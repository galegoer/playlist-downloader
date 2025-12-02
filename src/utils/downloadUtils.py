import os
import yt_dlp
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3
import urllib.parse
import requests

from utils.utils import use_regex
from utils.metaDataUtils import searchAppleMetaData, searchSpotifyMetaData
from utils.utils import _urlopen_safe
from utils.metaDataUtils import embed_coverart

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
            print('title: ', audio_title)
            
            if (not artist):
                artist = info.get('channel')
            
            # Remove any brackets with (Audio) or (Official Video) etc.
            audio_title = use_regex(audio_title)
            # If artist isn't included add it
            artwork = ""
            year = ""
            genre = ""
            track_num = 1
            track_total = 1
            if not artist in audio_title:
                audio_title += ' ' + artist.split(",")[0]
            try:
                audio_title, artist, album, track_num, track_total, genre, year, artwork = searchAppleMetaData(urllib.parse.quote_plus(audio_title), original_title=info.get("title"), original_artist=artist)
                apple_art = True
            except:
                audio_title, artist, album, track_num, track_total, genre, year, artwork = searchSpotifyMetaData(audio_title, original_title=info.get("title"), original_artist=artist)
            
            title = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

            # Populate artwork
            if artwork:
                if apple_art:
                    artwork = artwork.replace("100x100", "500x500")
                image_bytes = _urlopen_safe(artwork)
                embed_coverart(title, image_bytes, "jpg")

        # Kind of unnecessary but may be helpful if switching storage methods
        key = audio_title + " - " + artist
        print(key)

        mp3 = MP3(title, ID3=EasyID3)
        mp3['album'] = [album]
        mp3['artist'] = [artist]
        mp3['title'] = [audio_title]
        if year:
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
    
def download_playlist(link, key, save_path, start_num, end_num):
    failed = open("failed.txt", "a")
    
    playlist_id = link[link.find("=")+1:]
    final="https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+str(playlist_id)+"&key="+str(key)
    vidNum = 1
    
    r = requests.get(final)
    json = r.json()
    #print(json)
    
    totalRes = json["pageInfo"]["totalResults"]
    if(end_num == -1):
        #-1 means download all vids
        end_num = totalRes
    perPage = json["pageInfo"]["resultsPerPage"]
    try:
        nextToken = json["nextPageToken"]
    except:
        nextToken = None
    for result in range(0, totalRes, perPage):
        items = json["items"]
        for songId in range(0,len(items)):
            if not (vidNum >= start_num and vidNum <= end_num):
                if (vidNum < start_num):
                    vidNum += 1
                    continue
                else:
                    print("Done Downloading vids in range")
                    nextToken = None
                    break
            else:
                downloaded = False
                currId = items[songId]["contentDetails"]["videoId"]
                try:
                    for i in range(RETRY):
                        if downloadSong(currId, save_path) == 0:
                            downloaded = True
                            break
                    if not downloaded:
                        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                            info = ydl.extract_info(DOWNLOAD_LINK+currId, download=False)
                        artist = info.get('channel')
                        audio_title = info.get('title')
                        
                        failed.write("Failed downloading song: " + audio_title + ' - ' + artist + '\n')
                    vidNum += 1
                except:
                    continue

        if nextToken == None:
            break
        final = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+playlist_id+"&pageToken="+nextToken+"&key="+key
        r = requests.get(final)
        json = r.json()
        nextToken = json.get("nextPageToken")
    failed.close()