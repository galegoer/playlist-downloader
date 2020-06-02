import requests 
import subprocess
import shutil
from pytube import YouTube
 
SAVE_PATH = 'C:\\Users\\username\\Music\\GoodTimes\\' #CHANGE TO PATH WHERE YOU WANT TO SAVE THE SONGS

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
            for i in range(3):              #Retry 3 times if there are issues with the title
                if yt.title == 'YouTube':
                    yt = YouTube(downloadLink)
                else:
                    break            
            thumbnail_url = yt.thumbnail_url
        except Exception as e:
            print(e)
            print("Error with pytube for video :" + downloadLink+currId)
            continue
        d_video = yt.streams.filter(only_audio=True).first() #Change only_audio=True to file_extenstion='mp4' if you want mp4 files only
        #print(d_video)
        try: 
            #downloading the video
            title = yt.title.replace('\\', '').replace('/', '').replace(':', ' - ').replace('*', '-').replace('?', '').replace('<', '').replace('>', '').replace('|', '').replace('.', '') 
            dfile = d_video.download()
            temp_name = 'temp_name'+str(counter)+'.mp4'
            final_name = title+'.mp4'
            #adds album art
            subprocess.call(['ffmpeg', '-i', dfile, '-i', thumbnail_url, '-map', '1', '-map', '0', '-c', 'copy','-disposition:0', 'attached_pic', temp_name, '-loglevel', 'quiet'])
            subprocess.call(['rm', dfile])
            if d_video.title == 'YouTube':
                final_name = 'unknown_title'+str(counter)+'.mp4'
                counter += 1
            shutil.move(temp_name, SAVE_PATH+final_name)
            print("DOWNLOADED: " + final_name)
        except Exception as e:
            print(e)
            print("Error Downloading")
        
    if nextToken == None:
        break
    final = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+PLAYLIST_ID+"&pageToken="+nextToken+"&key="+KEY
    r = requests.get(final)
    json = r.json()
    nextToken = json.get("nextPageToken")