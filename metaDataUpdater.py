import os
import tkinter
from tkinter import filedialog
from get_cover_art import CoverFinder
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, ID3NoHeaderError
from mutagen.easyid3 import EasyID3
from tkinterdnd2 import TkinterDnD, DND_FILES, DND_TEXT
import requests
from io import BytesIO
from PIL import Image, ImageTk

from playlistDownloader import searchAppleMetaData

CANVAS_WIDTH = 150
CANVAS_HEIGHT = 150

image_data = None
image_format = None

def embed_coverart(file_path: str):
    try:
        mime = f"image/{image_format.lower()}" if image_format else "image/jpeg"
        print(mime)
        image_data.seek(0)
        tags = ID3(file_path)
        tags.add(APIC(
            encoding=3,  # UTF-8
            mime=mime,
            type=3,      # front cover
            desc='Cover',
            data=image_data.read()
        ))

        # Write a fresh v2.3 tag (iTunes-compatible)
        tags.save(file_path, v2_version=3)
        print(f"✅ Rewrote ID3v2.3 tags with new cover art: {os.path.basename(file_path)}")

    except Exception as e:
        print("Error embedding image into MP3:", e)

def load_current_cover(file_path: str):
    """Loads and displays current cover art (if present) from the MP3 file."""
    try:
        tags = ID3(file_path)
        for frame in tags.values():
            if isinstance(frame, APIC):
                img_data = BytesIO(frame.data)
                img = Image.open(img_data)
                img.thumbnail((CANVAS_WIDTH, CANVAS_HEIGHT))
                photo = ImageTk.PhotoImage(img)
                canvas.delete("all")
                canvas.create_image(CANVAS_WIDTH//2, CANVAS_HEIGHT//2, image=photo, anchor="center")
                canvas.image = photo
                print("Loaded existing cover art from file.")
                return
        print("No embedded cover art found.")
    except Exception as e:
        print("Error reading cover art:", e)

def drop(event):
    data = event.data.strip()
    if data.startswith('{') and data.endswith('}'):
        data = data[1:-1]
    if data.startswith('file:///'):
        data = data[8:]

    try:
        global image_data, image_format
        if data.startswith("http://") or data.startswith("https://"):
            print(f"Dropped URL: {data}")
            response = requests.get(data, timeout=5)
            image_data = BytesIO(response.content)
            image_format = Image.open(image_data).format
            image_data.seek(0)
        else:
            print(f"Dropped local file: {data}")
            with open(data, "rb") as f:
                image_data = BytesIO(f.read())
            image_format = Image.open(image_data).format
            image_data.seek(0)
        
        # Handle WEBP → JPEG conversion
        if image_format == "WEBP":
            img = Image.open(image_data).convert("RGB")
            converted = BytesIO()
            img.save(converted, format="JPEG")
            converted.seek(0)
            image_data = converted
            image_format = "JPEG"
        if image_format not in ["JPEG", "PNG"]:
            print("Unsupported image format.")
            raise Exception("Unsupported image format. Must be JPEG, PNG, or WEBP.")
    except Exception as e:
        print("Error loading image:", e)
        return

    try:
        img = Image.open(image_data)
        img.thumbnail((CANVAS_WIDTH, CANVAS_HEIGHT))
        photo = ImageTk.PhotoImage(img)
        canvas.delete("all")
        canvas.create_image(CANVAS_WIDTH//2, CANVAS_HEIGHT//2, image=photo, anchor="center")
        canvas.image = photo
        print("Displayed image on canvas.")
    except Exception as e:
        print("Error displaying image:", e)
        return

def searchMetaData():
    query = searchTerm.get()

    # track_name, artist, album, track_num, track_total, genre, year
    res = searchAppleMetaData(query)

    # TODO: Refactor duplicated code
    songTitle.delete(0, tkinter.END)
    songTitle.insert(0, res[0])
    
    songArtist.delete(0, tkinter.END)
    songArtist.insert(0, res[1])

    songAlbum.delete(0, tkinter.END)
    songAlbum.insert(0, res[2])

    songTracks.delete(0, tkinter.END)
    songTracks.insert(0, str(res[3]) + '/' + str(res[4]))

    songGenre.delete(0, tkinter.END)
    songGenre.insert(0, res[5])
    
    songYear.delete(0, tkinter.END)
    songYear.insert(0, res[6])

def handleClickEdit():

    filepath = app_window.sourceFolder
    
    title = songTitle.get()
    album = songAlbum.get()
    artist = songArtist.get()
    year = songYear.get()
    genre = songGenre.get()
    tracks = songTracks.get()
    enterInfo.config(text='Editing...')
    updateSong(filepath, title, artist, album, year, genre, tracks)

    enterInfo.config(text='Enter Info')
    
def handleCoverArt():
    
    filepath = app_window.sourceFolder
    
    finder = CoverFinder()
    # could add option for non nested
    finder.scan_folder(filepath)

def chooseFile():
    file = filedialog.askopenfilename(filetypes=[("mp3 files","*.mp3")]).replace("/", "\\")
    app_window.sourceFolder = os.path.abspath(file)
    
    print(app_window.sourceFolder)
    chooseFile.config(text='Editing file: ' + app_window.sourceFolder)
    
    load_current_cover(app_window.sourceFolder)
    
    # audiofile = eyed3.load(app_window.sourceFolder)
    audiofile = MP3(app_window.sourceFolder, ID3=EasyID3)

    songTitle.delete(0, tkinter.END)
    songTitle.insert(0, audiofile.get('title')[0])
    
    songAlbum.delete(0, tkinter.END)
    songAlbum.insert(0, audiofile.get('album')[0])
    
    songArtist.delete(0, tkinter.END)
    songArtist.insert(0, audiofile.get('artist')[0])

    songYear.delete(0, tkinter.END)
    songYear.insert(0, str(audiofile.get('date')[0]))

    songGenre.delete(0, tkinter.END)
    songGenre.insert(0, audiofile.get('genre')[0])

    songTracks.delete(0, tkinter.END)
    songTracks.insert(0, audiofile.get('tracknumber')[0])


def chooseDir():
    currdir = os.getcwd()
    app_window.sourceFolder = filedialog.askdirectory(parent=app_window, initialdir=currdir, title='Please select a directory').replace("/", "\\")
    chooseDir.config(text='Updating Cover Art in: ' + app_window.sourceFolder)
    
    print(app_window.sourceFolder)

def updateSong(file_path, title, artist, album, year, genre, tracks):
    
    # audiofile = eyed3.load(file_path)
    # audiofile.tag.artist = artist
    # audiofile.tag.album = album
    # audiofile.tag.title = title
    # audiofile.tag.album_artist = artist
    # audiofile.tag.track_num = track_num
    # audiofile.tag.track_total = track_total
    mp3 = MP3(file_path, ID3=EasyID3)
    mp3['album'] = [album]
    mp3['artist'] = [artist]
    mp3['title'] = [title]
    mp3['date'] = [year]
    mp3['genre'] = [genre]
    mp3['tracknumber'] = [tracks]
    mp3.save()
    
    if removeCoverArt.get():
        try:
            tags = ID3(file_path)
            # desc = audiofile.tag.images[0].description
            # audiofile.tag.images.remove(desc)
            tags.delall('APIC')
            tags.save()
        except:
            # has no picture
            print('file has no cover art: ', file_path)
    
    if coverArt.get():
        # Could change if you are editing files in a folder that may need it
        finder = CoverFinder(options={'cleanup': True})
        finder.scan_file(file_path)

    if True:
        embed_coverart(file_path)

if __name__ == "__main__":
                
    # app_window = tkinter.Tk()
    app_window = TkinterDnD.Tk()
    app_window.geometry("450x750")
    intro = tkinter.Label(text="Welcome\n Note: Will freeze upon start", fg="red")
    intro.pack()

    songTitleLabel = tkinter.Label(text='Enter the title of the song')
    songTitle = tkinter.Entry(width=50)
    songTitleLabel.pack()
    songTitle.pack()

    artistLabel = tkinter.Label(text='Enter the artist of the song')
    songArtist = tkinter.Entry(width=50)
    artistLabel.pack()
    songArtist.pack()
    
    albumLabel = tkinter.Label(text='Enter the album of the song')
    songAlbum = tkinter.Entry(width=50)
    albumLabel.pack()
    songAlbum.pack()

    yearLabel = tkinter.Label(text='Enter the year of the song/album')
    songYear = tkinter.Entry(width=50)
    yearLabel.pack()
    songYear.pack()  

    genreLabel = tkinter.Label(text='Enter the genre of the song/album')
    songGenre = tkinter.Entry(width=50)
    genreLabel.pack()
    songGenre.pack()  

    tracksLabel = tkinter.Label(text='Enter the song entry of the album in the form \'track_num/tracks_total\' format')
    songTracks = tkinter.Entry(width=50)
    tracksLabel.pack()
    songTracks.pack()

    searchLabel = tkinter.Label(text='Search song metadata through Apple Music')
    searchTerm = tkinter.Entry(width=50)
    searchLabel.pack()
    searchTerm.pack()

    searchMetaDataText = "Search and populate with metadata"
    searchMetaData = tkinter.Button(app_window, text=searchMetaDataText, bg="green", command=searchMetaData)
    searchMetaData.pack()
    
    removeCoverArt = tkinter.IntVar()
    removeCoverButton = tkinter.Checkbutton(text='Do you want to remove existing Cover Art?', variable=removeCoverArt, onvalue=True, offvalue=False)
    removeCoverButton.pack()    
    
    coverArt = tkinter.IntVar()
    coverArtButton = tkinter.Checkbutton(text='Do you want to download cover art?', variable=coverArt, onvalue=True, offvalue=False)
    coverArtButton.pack()

    dragAndDropLabel = tkinter.Label(app_window, text="Drag and drop an image to replace Cover Art below")
    dragAndDropLabel.pack()

    canvas = tkinter.Canvas(app_window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#ccc")
    canvas.pack(pady=10)

    canvas.drop_target_register(DND_FILES, DND_TEXT)
    canvas.dnd_bind("<<Drop>>", drop)
    
    chooseFileText = "Choose Song To Edit"
    chooseFile = tkinter.Button(app_window, text=chooseFileText, command=chooseFile)
    chooseFile.pack()
    
    enterInfo = tkinter.Button(app_window, text='Start Editing Song', bg="red", command=handleClickEdit)
    enterInfo.pack()
    
    chooseDirText = "Choose Folder To Add Cover Art To (Will Work Nested)"
    chooseDir = tkinter.Button(app_window, text=chooseDirText, command=chooseDir)
    chooseDir.pack()
    
    startCover = tkinter.Button(app_window, text='Add Cover Art to Folder', bg="red", command=handleCoverArt)
    startCover.pack()
    
    app_window.mainloop()