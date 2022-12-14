import os
import tkinter
from tkinter import filedialog
from get_cover_art import CoverFinder
import eyed3

def handleClickEdit():

    filepath = app_window.sourceFolder
    
    title = songTitle.get()
    album = songAlbum.get()
    artist = songArtist.get()
    enterInfo.config(text='Editing...')
    updateSong(filepath, title, artist, album, coverArt.get())

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
    
    audiofile = eyed3.load(app_window.sourceFolder)
    print(audiofile.tag.title)
    songTitle.delete(0, tkinter.END)
    songTitle.insert(0, audiofile.tag.title)
    
    print(audiofile.tag.album)
    songAlbum.delete(0, tkinter.END)
    songAlbum.insert(0, audiofile.tag.album)    
    
    print(audiofile.tag.artist)
    songArtist.delete(0, tkinter.END)
    songArtist.insert(0, audiofile.tag.artist)        
    
    
    
def chooseDir():
    currdir = os.getcwd()
    app_window.sourceFolder = filedialog.askdirectory(parent=app_window, initialdir=currdir, title='Please select a directory').replace("/", "\\")
    chooseDir.config(text='Updating Cover Art in: ' + app_window.sourceFolder)
    
    print(app_window.sourceFolder)

def updateSong(filepath, title, artist, album, coverArt):
    
    audiofile = eyed3.load(filepath)
    audiofile.tag.artist = artist
    audiofile.tag.album = album
    audiofile.tag.title = title
    
    if removeCoverArt:
        try:
            desc = audiofile.tag.images[0].description
            audiofile.tag.images.remove(desc)
        except:
            # has no picture
            print('file has no cover art: ', filepath)
    
    audiofile.tag.save()
    
    if coverArt:
        # Could change if you are editing files in a folder that may need it
        finder = CoverFinder(options={'cleanup': True})
        finder.scan_file(filepath)

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
    
    chooseDirText = "Chose Folder To Add Cover Art To (Will Work Nested)"
    chooseDir = tkinter.Button(app_window, text=chooseDirText, command=chooseDir)
    chooseDir.pack()
    
    startCover = tkinter.Button(app_window, text='Add Cover Art to Folder', bg="red", command=handleCoverArt)
    startCover.pack()
    
    app_window.mainloop()