# Playlist-downloader

This is a YouTube playlist downloader that I made after realizing pytube already has the function to do half the work I did.

# Requirements
- Python 3.8
- pytube (can be installed using pip or from the web)
- YouTube Data API v3 key

# Steps to download
1. Open the playlist-downloader.py file and edit the SAVE_PATH line on line 5. Set it to the directory you would like to save your songs to. (Example: 'C:\\Users\\USERNAME\\Music\\MyPlaylist\\')

2. Type in the link to your playlist on line 7 and make sure it is set to Public on YouTube. (Example playlist: "https://www.youtube.com/playlist?list=PLArQ6Xij15ikMnefk5BL5PwdTLfqmtMNz")

3. Here is where you need the YouTube Data API v3 key. Type the key into line 8.
You will need to sign up for a key using this link if you do not already have one.
https://console.developers.google.com/


# Known issues
- If you are using this to transfer songs via iTunes there is an issue with the headers which will make the song appear longer than it actually is under length. (FIX IN PROGRESS)
- Some songs may download without knowing their title so you may have to manually rename them, the audio still works but the song title cannot be found. These will be titled 'unknown_title' followed by a number.
- There is a method in pytube that downloads a playlist for you but I already coded this program before I realized that so this entire script ends up being just extra work

Pytube may have an issue as YouTube sometimes changes its key names. You may follow this branch of the revised code 
https://github.com/nficano/pytube/pull/643
or if you would like to fix the issue yourself at line 299 of extract.py (located where you installed pytube)

```python
299     except KeyError:
300              cipher_url = [
301                parse_qs(formats[i]["cipher"]) for i, data in enumerate(formats)
302              ]
```

Change the string "cipher" to "signatureCipher". Then save and rerun the program.
