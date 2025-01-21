import requests
import os
import tkinter
from tkinter import filedialog
import youtube_dl
from get_cover_art import CoverFinder
import eyed3
from dotenv import load_dotenv

from playlistDownloader import download_playlist

# Run this file however often you would like when there are updates to your playlist

# Include a text file called lastTotal.txt that only has the latest number of songs in the playlist,
# if you need to download for example the latest 10 and there are 50 you would put in 40, if you want to
# download all set the number to 0

LINK = '' # Fill in with your public playlist link
KEY = '' # Fill in with your YouTube Data API key
SAVE_PATH = "" # Change to path you want to save songs in
START_NUM = 1

if __name__ == "__main__":
    load_dotenv()
    lastTotalFile = open("lastTotal.txt", "r")
    lastTotal = int(lastTotalFile.read())
    lastTotalFile.close()
        
    playlist_id = LINK[LINK.find("=")+1:]
    final="https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+str(playlist_id)+"&key="+str(KEY)
    
    r = requests.get(final)
    json = r.json()
    
    totalRes = json["pageInfo"]["totalResults"]
    print('TOTAL: ', totalRes)
    print('LAST TOTAL: ', lastTotal)
    end_num = totalRes - lastTotal
    
    print('NUMBER OF SONGS TO DOWNLOAD: ', end_num)
    
    if(end_num <= 0):
        #no new songs
        print('No new songs to download')
    else:
        download_playlist(LINK, KEY, SAVE_PATH, START_NUM, end_num)
    newTotal = open("lastTotal.txt", "w")
    newTotal.write(str(totalRes))
    newTotal.close()