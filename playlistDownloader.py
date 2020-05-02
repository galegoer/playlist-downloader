import requests 
from pytube import YouTube 
import os
 
SAVE_PATH = "" #CHANGE TO PATH WHERE YOU WANT TO SAVE THE FILES

playlistLink = "" #PUT YOUR PUBLIC PLAYLIST LINK HERE
key="" #insert a Youtube Data API v3 key here
downloadLink = "https://www.youtube.com/watch?v="

PLAYLIST_ID = playlistLink[playlistLink.find("=")+1:]
final="https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+PLAYLIST_ID+"&key="+key

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
            print(yt.title)
        except: 
            print("Connection Error") 
        d_video = yt.streams.filter(only_audio=True).first() #Change only_audio=True to file_extenstion='mp4' if you want mp4 files only
        print(d_video)
        try: 
            #downloading the video 
            dfile = d_video.download()
            os.rename(dfile, SAVE_PATH+yt.title)
            
            #os.rename(dfile, SAVE_PATH+yt.title+'.mp3') #THIS is if you want strictly mp3 files, uncomment this and comment out above line
            
            print("DOWNLOADED: "+ yt.title)
        except: 
            print("Error Downloading")
        
    if nextToken == None:
        break
    final = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+PLAYLIST_ID+"&pageToken="+nextToken+"&key="+key
    r = requests.get(final)
    json = r.json()
    nextToken = json.get("nextPageToken")