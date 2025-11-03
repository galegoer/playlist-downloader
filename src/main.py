import sys
import requests
from dotenv import load_dotenv

from config.settings import LINK, KEY, SAVE_PATH, START_NUM, debugger
from utils.downloader import download_playlist

# Run this file however often you would like when there are updates to your playlist

# Include a text file called lastTotal.txt that only has the latest number of songs in the playlist,
# if you need to download for example the latest 10 and there are 50 you would put in 40, if you want to
# download all set the number to 0

if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) == 2:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]

        lastTotalFile = open("lastTotal.txt", "r")
        lastTotal = int(lastTotalFile.read())
        lastTotalFile.close()
            
        playlist_id = LINK[LINK.find("=")+1:]
        final="https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId="+str(playlist_id)+"&key="+str(KEY)
        
        r = requests.get(final)
        json = r.json()
        
        totalRes = json["pageInfo"]["totalResults"]
        end_num = totalRes - lastTotal
        
        debugger.write(f"NUMBER OF SONGS TO DOWNLOAD: {end_num}\n")
        
        if(end_num <= 0):
            debugger.write('No new songs to download\n')
        else:
            download_playlist(LINK, KEY, SAVE_PATH, START_NUM, end_num)
        newTotal = open("lastTotal.txt", "w")
        newTotal.write(str(totalRes))
        newTotal.close()
    else:
        print("More or less than 2 arguments were provided please provide a playlist link and YT API key")