import requests
from get_cover_art import CoverFinder
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3
from io import BytesIO
from PIL import Image

def embed_coverart(file_path: str, image_data: BytesIO, image_format: str):
    try:
        # Convert image to JPEG always (iTunes requirement)
        img = Image.open(BytesIO(image_data)).convert("RGB")
        jpeg_buffer = BytesIO()
        img.save(jpeg_buffer, format="JPEG")
        jpeg_bytes = jpeg_buffer.getvalue()

        try:
            tags = ID3(file_path)
        except error:
            tags = ID3()
        # Remove old APIC frames (iTunes ignores duplicates)
        for key in list(tags.keys()):
            if key.startswith("APIC"):
                del tags[key]

        tags.add(APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=jpeg_bytes
        ))

        # Save as proper ID3v2.3 (very important)
        tags.save(file_path, v2_version=3)
        # print(image_format)
        # print(image_data)
        # mime = f"image/{image_format.lower()}" if image_format else "image/jpeg"
        # image_data.seek(0)
        # tags = ID3(file_path)
        # tags.add(APIC(
        #     encoding=3,  # UTF-8
        #     mime=mime,
        #     type=3,      # front cover
        #     desc='Cover',
        #     data=image_data.read()
        # ))

        # # Write a fresh v2.3 tag (iTunes-compatible)
        # tags.save(file_path, v2_version=3)
        # print(f"✅ Rewrote ID3v2.3 tags with new cover art")

    except Exception as e:
        print("Error embedding image into MP3:", e)

def get_current_cover(file_path: str):
    """Loads and displays current cover art (if present) from the MP3 file."""
    try:
        tags = ID3(file_path)
        for frame in tags.values():
            if isinstance(frame, APIC):
                img_data = BytesIO(frame.data)
                img = Image.open(img_data)
                img_name = frame.mime.split("/")[1]
                print('img_name: ', img_name)
                print("Loaded existing cover art from file.")
                return img, img_data, img_name
        print("No embedded cover art found.")
    except Exception as e:
        print("Error reading cover art:", e)

def searchAppleMetaData(title):
    debugger = open("debugger.txt", "a")
    debugger.write("Searched title: " + title + '\n')
    query = 'https://itunes.apple.com/search?media=music&term={}&limit=3'.format(title)
    result = requests.get(query).json()

    try:
        track = result['results'][0]
        debugger.write("Results: " + str(result['results']))
        track_name = track['trackName']
        artist = track['artistName']
        album = track['collectionName']
        track_num = track['trackNumber']
        track_total = track['trackCount']
        genre = track['primaryGenreName']
        year = track['releaseDate'][:4]
        artwork = track['artworkUrl100']
        return track_name, artist, album, track_num, track_total, genre, year, artwork
    except:
        print('Could not find: ', title)

def updateSong(file_path, title, artist, album, year, genre, tracks):
    mp3 = MP3(file_path, ID3=EasyID3)
    mp3['album'] = [album]
    mp3['artist'] = [artist]
    mp3['title'] = [title]
    mp3['date'] = [year]
    mp3['genre'] = [genre]
    mp3['tracknumber'] = [tracks]
    mp3.save()

def find_cover_art(filepath: str):
    finder = CoverFinder(options={'cleanup': True})
    finder.scan_file(filepath)

def convert_webp_to_jpg(filepath: str):
    img = Image.open(filepath)
    img = img.convert("RGB")
    img.save(filepath)