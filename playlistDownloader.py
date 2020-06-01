import requests 
import os
from pytube import YouTube
 
SAVE_PATH = 'C:\\Users\\username\\Music\\myplaylist\\' #CHANGE TO PATH WHERE YOU WANT TO SAVE THE SONGS

PLAYLIST_LINK = "https://www.youtube.com/playlist?list=PLArQ6Xij15ikMnefk5BL5PwdTLfqmtMNz" #PUT YOUR PUBLIC PLAYLIST LINK HERE
KEY="" #insert a Youtube Data API v3 key here


downloadLink = "https://www.youtube.com/watch?v="

PLAYLIST_ID = PLAYLIST_LINK[PLAYLIST_LINK.find("=")+1:]
final="https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+PLAYLIST_ID+"&key="+KEY
counter = 0


r = requests.get(final)
json = r.json()

totalRes = json["pageInfo"]["totalResults"]
perPage = json["pageInfo"]["resultsPerPage"]
nextToken = json["nextPageToken"]
for result in range(0, totalRes, perPage):
    items = json["items"]
    for songId in range(0,len(items)):
        currId = items[songId]["contentDetails"]["videoId"]
        try:
            yt = YouTube(downloadLink+currId)
        except Exception as e:
            print(e)
            print("Error with pytube for video :" + downloadLink+currId)
            continue
        d_video = yt.streams.filter(only_audio=True).first() #Change only_audio=True to file_extenstion='mp4' if you want mp4 files only
        #print(d_video)
        try: 
            #downloading the video
            dfile = d_video.download(SAVE_PATH)
            if d_video.title == 'YouTube':
                unknown_name = 'unknown_title'+str(counter)+'.mp4'
                os.rename(dfile, SAVE_PATH+unknown_name)
                counter += 1
                print("DOWNLOADED: " + unknown_name) 
            else:
                print("DOWNLOADED: " + yt.title)
        except Exception as e:
            print(e)
            print("Error Downloading")
        
    if nextToken == None:
        break
    final = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+PLAYLIST_ID+"&pageToken="+nextToken+"&key="+KEY
    r = requests.get(final)
    json = r.json()
    nextToken = json.get("nextPageToken")