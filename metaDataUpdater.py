import os
import tkinter
from tkinter import filedialog
from get_cover_art import CoverFinder
import eyed3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3

from playlistDownloader import searchAppleMetaData

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
    updateSong(filepath, title, artist, album, coverArt.get(), year, genre, tracks)

    enterInfo.config(text='Enter Info')
    
def handleCoverArt():
    
    filepath = app_window.sourceFolder
    
    finder = CoverFinder()
    # could add option for non nested
    finder.scan_folder(filepath)

def chooseFile():
    currdir = os.getcwd()
    
    file = filedialog.askopenfilename(filetypes=[("mp3 files","*.mp3")]).replace("/", "\\")
    app_window.sourceFolder = os.path.abspath(file)
    
    print(app_window.sourceFolder)
    chooseFile.config(text='Editing file: ' + app_window.sourceFolder)
    
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

def updateSong(file_path, title, artist, album, removeCoverArt, year, genre, tracks):
    
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
    
    if removeCoverArt:
        try:
            tags = ID3(file_path)
            # desc = audiofile.tag.images[0].description
            # audiofile.tag.images.remove(desc)
            tags.delall('APIC')
            tags.save()
        except:
            # has no picture
            print('file has no cover art: ', file_path)
    
    if coverArt:
        # Could change if you are editing files in a folder that may need it
        finder = CoverFinder(options={'cleanup': True})
        finder.scan_file(file_path)

if __name__ == "__main__":
                
    app_window = tkinter.Tk()
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
    coverArtButton = tkinter.Checkbutton(text='Do you want to download cover art as well?', variable=coverArt, onvalue=True, offvalue=False)
    coverArtButton.pack()
    
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