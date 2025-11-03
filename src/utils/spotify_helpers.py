import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def searchSpotifyMetaData(title):
    
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