import requests

from config.settings import debugger

def searchAppleMetaData(title):
    debugger.write(f"Searched title: {title} \n")
    query = 'https://itunes.apple.com/search?media=music&term={}&limit=3'.format(title)
    result = requests.get(query).json()

    try:
        track = result['results'][0]
        # debugger.write(f"Results: {str(result['results'])})
        track_name = track['trackName']
        artist = track['artistName']
        album = track['collectionName']
        track_num = track['trackNumber']
        track_total = track['trackCount']
        genre = track['primaryGenreName']
        year = track['releaseDate'][:4]
        return track_name, artist, album, track_num, track_total, genre, year
    except:
        debugger.write("Could not find: {title}\n")