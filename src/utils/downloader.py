import os
import urllib.parse

import yt_dlp
import requests
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3 
from get_cover_art import CoverFinder

from utils.apple_helpers import searchAppleMetaData
from utils.helpers import use_regex
from config.settings import YDL_OPTS, RETRY, DOWNLOAD_LINK, debugger

def download_song(currId, save_path):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(DOWNLOAD_LINK+currId, download=True)
            album = info.get('album')
            artist = info.get('artist')
            audio_title = info.get('title')
            
            if (not artist):
                artist = info.get('channel') # Assumes you are retrieving from official channel
            
            # Remove any brackets with (Audio) or (Official Video) etc.
            audio_title = use_regex(audio_title).strip()
            # If artist isn't included add it
            if not artist in audio_title:
                audio_title += ' ' + artist.split(",")[0] # uses first artist if multiple
            audio_title, artist, album, track_num, track_total, genre, year = searchAppleMetaData(urllib.parse.quote_plus(audio_title))
            title = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

        # TODO: if something fails it will just not update any metadata? not sure if it will show that file failed since it was techincally downloaded
        mp3 = MP3(title, ID3=EasyID3)
        mp3['album'] = [album]
        mp3['artist'] = [artist]
        mp3['title'] = [audio_title]
        mp3['date'] = [year]
        mp3['genre'] = [genre]
        mp3['tracknumber'] = [str(track_num)+'/'+str(track_total)]
        mp3.save()
        
        final_name = title.split(' [')[0]+'.mp3'
        
        os.rename(title, save_path+final_name)
        debugger.write(f"DOWNLOADED: {final_name}\n")
        return 0
    except Exception as e:
        debugger.write(f"Exception: {e}\n")
        return -1


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
                    debugger.write("Done Downloading vids in range\n")
                    nextToken = None
                    break
            else:
                downloaded = False
                currId = items[songId]["contentDetails"]["videoId"]
                try:
                    for i in range(RETRY):
                        if download_song(currId, save_path) == 0:
                            downloaded = True
                            break
                    if not downloaded:
                        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                            info = ydl.extract_info(DOWNLOAD_LINK+currId, download=False)
                        artist = info.get('channel')
                        audio_title = info.get('title')
                        
                        debugger.write(f"Failed downloading song: {audio_title} - {artist} \n")
                    vidNum += 1
                except:
                    continue

        if nextToken == None:
            break
        final = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+playlist_id+"&pageToken="+nextToken+"&key="+key
        r = requests.get(final)
        json = r.json()
        nextToken = json.get("nextPageToken")

    finder = CoverFinder(options={'cleanup': True})
    
    # Make sure iTunes is not open
    finder.scan_folder(save_path)
    failed.close()