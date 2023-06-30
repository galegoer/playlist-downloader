import requests
import os
import tkinter
from tkinter import filedialog
import youtube_dl
from get_cover_art import CoverFinder
import eyed3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import csv

RETRY = 3
DOWNLOAD_LINK = "https://youtube.com/watch?v="
YDL_OPTS = {
    'debug_printtraffic': 'false',
    'format': 'bestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',},
    ],
}

def handleClick():
    print("clicked")
    link = playlistLink.get()
    key = apiKey.get()
    try:
        save_path = app_window.sourceFolder+'\\'
    except:
        save_path = os.getcwd()+'\\'
    print(save_path)
    if not allVideos.get():
        print("NOT ALL VIDS")
        start_num = int(vidStartNum.get())
        end_num = int(vidEndNum.get())
        enterInfo.config(text='Downloading...')        
        download_playlist(link, key, save_path, start_num, end_num)
    else:
        print("ALL VIDS")
        enterInfo.config(text='Downloading... ')
        download_playlist(link, key, save_path, 1, -1)
    enterInfo.config(text='Enter Info')   

def searchMetaData(title):
    
    result = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials()).search(title, 3, 0)
    try:
        track = result['tracks']['items'][0]
        artist = track['artists'][0]['name']
        album = track['album']['name']
        # not sure if this guaranteed but if we don't want the name of features
        audio_title = track['name'].split("(")
        if audio_title[0] == "":
            audio_title = track['name']
        if audio_title[-1] == ' ':
            audio_title = audio_title[:-1]
        if audio_title[0][-1] == ' ':
            audio_title = audio_title[0][:-1]
            return audio_title, artist, album
        return audio_title[0], artist, album
    except:
        print('Could not find:', title)
    
    
def download_song(currId, save_path):
    try:
        with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(DOWNLOAD_LINK+currId, download=True)
            album = info.get('album')
            artist = info.get('artist')
            audio_title = info.get('title')
            if (artist and len(artist.split(',')) > 1) or (not artist):
                # back up if no information search through spotify might be an easier way but this works for now
                artist = info.get('channel')
                # add artist/channel name in case song title could be interpreted as another song
                audio_title, artist, album = searchMetaData(audio_title + ' ' + artist)
            title = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            print("TITLE:", title)

        # Kind of unnecessary but may be helpful if switching storage methods
        key = audio_title + " - " + artist
        print(key)

        with open("C:\\Users\\Eric's PC\\JenkinsJobs\\daily-tiktok\\remaining_songs.csv", mode='a', encoding='utf-8') as song_file:
            song_file_writer = csv.writer(song_file, delimiter=",", quotechar='"', lineterminator="\n")
            song_file_writer.writerow([key, audio_title, artist, album])

        audiofile = eyed3.load(title)
        audiofile.tag.artist = artist
        audiofile.tag.album = album
        # not sure if needed
        audiofile.tag.title = audio_title
        
        audiofile.tag.save()
        
        final_name = title.rsplit('-'+currId, 1)[0] + '.mp3'
        #adds album art
        #os.system('ffmpeg -i "' + dfile + '" -i "' + thumbnail_url + '" -q:a 0 -map a -c copy -disposition:0 attached_pic "' + temp_name + '" -loglevel quiet')
        
        os.rename(title, save_path+final_name)
        print("DOWNLOADED:", final_name)
        return 0
    except Exception as e:
        print("Exception:", e)
        return -1


def download_playlist(link, key, save_path, start_num, end_num):
    video_number = 0
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
                for i in range(RETRY):
                    if download_song(currId, save_path) == 0:
                        downloaded = True
                        break
                if not downloaded:
                    with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
                        info = ydl.extract_info(DOWNLOAD_LINK+currId, download=False)
                    artist = info.get('channel')
                    audio_title = info.get('title')
                    
                    failed.write("Failed downloading song: " + audio_title + ' - ' + artist + '\n')
                vidNum += 1
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
    
def chooseDir():
    currdir = os.getcwd()
    app_window.sourceFolder = filedialog.askdirectory(parent=app_window, initialdir=currdir, title='Please select a directory').replace("/", "\\")
    chooseDir.config(text='Saving to: ' + app_window.sourceFolder)
    print(app_window.sourceFolder)

if __name__ == "__main__":
    load_dotenv()
    app_window = tkinter.Tk()
    intro = tkinter.Label(text="Welcome\n Note: Will freeze upon download but notifications will be sent upon each download", fg="red")
    intro.pack()

    apiKeyLabel = tkinter.Label(text='Enter a Youtube Data API v3 key')
    apiKey = tkinter.Entry(width=50)
    apiKeyLabel.pack()
    apiKey.pack()

    linkLabel = tkinter.Label(text='Enter a public Youtube playlist link')
    playlistLink = tkinter.Entry(width=50)
    linkLabel.pack()
    playlistLink.pack()
    allVideos = tkinter.IntVar()
    allVids = tkinter.Checkbutton(text='Do you want to download all the videos?', variable=allVideos, onvalue=True, offvalue=False)
    allVids.pack()
    startLabel = tkinter.Label(text='Enter the video number you want to start downloading from')
    startLabel.pack()
    vidStartNum = tkinter.Entry(width=50)
    startLabel.pack()
    vidStartNum.pack()
    endLabel = tkinter.Label(text='Enter the ending video number you want to end at (this number is included)')
    vidEndNum = tkinter.Entry(width=50)
    endLabel.pack()
    vidEndNum.pack()
    chooseDirText = "Chose Folder To Save To"
    chooseDir = tkinter.Button(app_window, text=chooseDirText, command=chooseDir)
    chooseDir.pack()
    enterInfo = tkinter.Button(app_window, text='Start Download', bg="red", command=handleClick)
    enterInfo.pack()
    app_window.mainloop()