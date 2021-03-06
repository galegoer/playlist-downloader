import requests
import os
#from decouple import config
#from pytube import YouTube
import tkinter
from tkinter import filedialog
import youtube_dl
from win10toast import ToastNotifier

def handleClick():
    print("clicked")
    link = playlistLink.get()
    key = apiKey.get()
    try:
        save_path = app_window.sourceFolder+'/'
    except:
        save_path = ''
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

def download_playlist(link, key, save_path, start_num, end_num):
    video_number = 0
    downloadLink = "https://youtube.com/watch?v="
    
    playlist_id = link[link.find("=")+1:]
    final="https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+str(playlist_id)+"&key="+str(key)
    vidNum = 1
    
    r = requests.get(final)
    json = r.json()
    
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
                currId = items[songId]["contentDetails"]["videoId"]
                try:
                    ydl_opts = {
                        'debug_printtraffic': 'false',
                        'writethumbnail': 'True',                        
                        'format': 'bestaudio',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',},
                            {'key': 'EmbedThumbnail',},
                        ],
                    }
                    
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(downloadLink+currId, download=True)
                        print(info)
                        title = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                        print("TITLE: " + title)
                    thumbnail_url = 'https://i.ytimg.com/vi/'+currId+'/hqdefault.jpg'
                
                    #downloading the video
                    #title = title.replace('\\', '').replace('/', '').replace(':', ' - ').replace('*', '-').replace('?', '').replace('<', '').replace('>', '').replace('|', '').replace('.', '').replace('\'', '').replace('\"', '') 
                    #temp_name = 'temp_name'+str(vidNum)+'.mp3'
                    final_name = title.rsplit('-', 1)[0] + '.mp3'
                    #adds album art
                    #os.system('ffmpeg -i "' + dfile + '" -i "' + thumbnail_url + '" -q:a 0 -map a -c copy -disposition:0 attached_pic "' + temp_name + '" -loglevel quiet')
                    
                    os.rename(title, save_path+final_name)
                    toaster.show_toast("Playlist downloader", 'downloaded: '+final_name, duration=3, threaded=True)                    
                    print("DOWNLOADED: " + final_name)
                except Exception as e:
                    print(e)
                    print("Error Downloading")
                vidNum += 1
        if nextToken == None:
            break
        final = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+playlist_id+"&pageToken="+nextToken+"&key="+key
        r = requests.get(final)
        json = r.json()
        nextToken = json.get("nextPageToken")
    
def chooseDir():
    currdir = os.getcwd()
    app_window.sourceFolder = filedialog.askdirectory(parent=app_window, initialdir=currdir, title='Please select a directory')
    chooseDir.config(text='Saving to: ' + app_window.sourceFolder)
    print(app_window.sourceFolder)

if __name__ == "__main__":
    toaster = ToastNotifier()
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