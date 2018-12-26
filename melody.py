# ======================================================================================================================
# Melody v1.0
# Python | TkInter | PyGame | Threading
# Developed by: Aman Chadha
#
# Developed and tested on Python 3
#
# Thanks to Attreya Bhatt for the help!
# ======================================================================================================================

import os
import threading
import time

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

try:
    from ttkthemes import themed_tk as tk
except:
    print("Trying to install required module: ttkthemes")
    os.system('python3 -m pip install ttkthemes')
    from ttkthemes import themed_tk as tk

try:
    from mutagen.mp3 import MP3
except:
    print("Trying to install required module: mutagen")
    os.system('python3 -m pip install mutagen')
    from mutagen.mp3 import MP3

try:
    from pygame import mixer
except:
    print("Trying to install required module: pygame")
    os.system('python3 -m pip install pygame')
    from pygame import mixer

# ERROR CODE(S)
FILE_NOT_SELECTED = 1

# KNOBS
DEFAULT_VOLUME = 70

# STATE INFORMATION
paused = FALSE
muted = FALSE

def aboutMelody():
    messagebox.showinfo('Melody v1.0',
                        'A music player built using Python Tkinter',
                        'www.amanchadha.com | github.com/amanchadha')

def browseFile(playListBox):
    """ Show the "Open File" dialog box to obtain a handle to music file. """

    pathToFile = filedialog.askopenfilename()

    if len(pathToFile): #pathToFile is not blank (i.e., the user did not cancel the open dialog box)
        addToPlaylist(playListBox, pathToFile)
        mixer.music.queue(pathToFile)

    return pathToFile

def addToPlaylist(playListBox, pathToFile):
    """ Add the music file to the playlist. """

    global playList
    index = 0

    # playListBox - contains just the filename
    playListBox.insert(index, os.path.basename(pathToFile))

    # playList - contains the full path + filename
    playList.insert(index, pathToFile)

def removeSong(playListBox):
    """ Delete the music file from the playlist. """

    selectedSong = int(playListBox.curselection()[0])
    playListBox.delete(selectedSong)
    playList.pop(selectedSong)

def showDetails(playSong):
    """ Delete the music file from the playlist. """

    # get the extension of the file
    totalLength = MP3(playSong).info.length if os.path.splitext(playSong)[1] == '.mp3' else mixer.Sound(playSong).get_length()

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(totalLength, 60)
    mins, secs = round(mins), round(secs)
    timeFormat = '{:02d}:{:02d}'.format(mins, secs)
    lengthLabel['text'] = "Total Length" + ' - ' + timeFormat

    # start a thread that can handle the down-counter for us
    # doing the down-counter in the main threads keeps the main thread spinning until the song finishes which is something we don't want
    t1 = threading.Thread(target=startCount, args=(totalLength,))
    t1.start()

def startCount(totalLength):
    global paused
    currentTime = totalLength

    # mixer.music.get_busy() returns False when the music isn't playing
    while mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(currentTime, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            currentTimeLabel['text'] = "Time Remaining" + ' - ' + timeformat
            time.sleep(1)
            currentTime -= 1

def playMusic(playList, playListBox, chosenPlayListItem=False):
    """ This function goes three ways:
        1. Resume music if paused
        2. If a music file is loaded in the playlist (and selected), it will start playing
        3. If a music file isn't loaded in the playlist, it will ask you to load one
    """
    global paused

    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music resumed"
        paused = FALSE
    elif len(playList):
        stopMusic()
        time.sleep(1)
        selectedSong = int(playListBox.curselection()[0]) if chosenPlayListItem is False else chosenPlayListItem
        songToBePlayed = playList[selectedSong]
        mixer.music.load(songToBePlayed)
        try:
            mixer.music.play()
        except:
            messagebox.showerror('File not found', 'Melody could not find the file. Please check again.')
        statusbar['text'] = "Playing music: " + os.path.basename(songToBePlayed)
        showDetails(songToBePlayed)
    else:
        if len(browseFile(playListBox)): # check if return value is not blank (i.e., the user did not cancel the open dialog box)
            playMusic(playList, playListBox, chosenPlayListItem=0)

def stopMusic():
    mixer.music.stop()
    statusbar['text'] = "Music stopped"

def pauseMusic():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music paused"

def rewindMusic(playList, playListBox):
    print(0 if len(playList) == 1 else (int(playListBox.curselection()[0])-1))
    playMusic(playList, playListBox, int(playListBox.curselection()[0])-1 if (int(playListBox.curselection()[0])-1) >= 0 else 0)

def forwardMusic(playList, playListBox):
    print(0 if len(playList) == 1 else ((int(playListBox.curselection()[0])+1) % len(playList)))
    playMusic(playList, playListBox, (int(playListBox.curselection()[0])+1) % len(playList))

def setVolume(volumeLevel):
    # mixer.music.set_volume() takes a float value belonging to [0, 1]
    mixer.music.set_volume(float(volumeLevel) / 100)

def muteMusic():
    """ Mute/unmute the Music. """
    global muted
    if muted:  # unmute the music
        mixer.music.set_volume(0.7)
        volumeBtn.configure(image=unmutePhoto)
        scale.set(70)
        muted = FALSE
    else:  # mute the music
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        scale.set(0)
        muted = TRUE

def exitWindow():
    """ Window close event handler to stop music before destroying window resources """
    stopMusic()
    root.destroy()

if __name__ == "__main__":
    # setup Tk themes
    root = tk.ThemedTk()
    root.get_themes()           # returns a list of all themes that can be set
    root.set_theme("aqua")  # sets an available theme
    root.configure(background="#868d99")

    # root window   - status bar, left frame, right frame
    # left frame    - listbox (playlist)
    # right frame   - top frame, middle frame and bottom frame

    # setup the status bar
    statusbar = ttk.Label(root, text="Welcome to Melody v1.0 | www.amanchadha.com", relief=SUNKEN, anchor=W, font='Helvetica 10')
    statusbar.pack(side=BOTTOM, fill=X)

    # setup the menubar
    menubar = Menu(root)
    root.config(menu=menubar)

    # create the File submenu
    fileMenu = Menu(menubar, tearoff=0)
    fileMenu.add_command(label="Open", command=browseFile)
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit", command=exitWindow)
    menubar.add_cascade(label="File", menu=fileMenu)

    # create the Help submenu
    helpMenu = Menu(menubar, tearoff=0)
    helpMenu.add_command(label="About Us", command=aboutMelody)
    menubar.add_cascade(label="Help", menu=helpMenu)

    # set window title and icon
    root.title("Melody")
    melodyIcon = PhotoImage(file=os.path.join(os.getcwd(), 'assets/melody.png'))
    root.tk.call('wm', 'iconphoto', root._w, melodyIcon)

    # initialize the mixer
    mixer.init()

    # initialize the playlist
    playList = []

    # LEFT FRAME
    leftFrame = Frame(root, bg="#868d99")
    leftFrame.pack(side=LEFT, padx=30, pady=30)

    # playlist
    playListBox = Listbox(leftFrame, bg="#ECECEC")
    playListBox.pack()

    # add/remove song buttons
    addPhoto = PhotoImage(file=r'assets/add.png')
    addBtn = ttk.Button(leftFrame, image=addPhoto, command=lambda: browseFile(playListBox))
    addBtn.pack(side=LEFT, padx=2, ipadx=2, ipady=3)
    removePhoto = PhotoImage(file=r'assets/remove.png')
    removeBtn = ttk.Button(leftFrame, image=removePhoto, command=lambda: removeSong(playListBox))
    removeBtn.pack(side=LEFT, ipadx=2, ipady=3)

    # RIGHT FRAME
    rightFrame = Frame(root, bg="#ECECEC")
    rightFrame.pack(side=RIGHT, padx=30, pady=30)

    # top frame for displaying total length and current time
    topFrame = Frame(rightFrame, bg="#ECECEC")
    topFrame.pack()

    lengthLabel = ttk.Label(topFrame, text='Total Length: --:--')
    lengthLabel.pack(pady=10)

    currentTimeLabel = ttk.Label(topFrame, text='Time Remaining: --:--')
    currentTimeLabel.pack()

    # middle frame for play, stop, pause buttons
    middleFrame = Frame(rightFrame, bg="#ECECEC")

    # play button
    playPhoto = PhotoImage(file=r'assets/play.png')
    playBtn = ttk.Button(middleFrame, image=playPhoto, command=lambda: playMusic(playList, playListBox))
    playBtn.grid(row=0, column=0, padx=10, ipady=5, ipadx=5)

    # stop button
    stopPhoto = PhotoImage(file=r'assets/stop.png')
    stopBtn = ttk.Button(middleFrame, image=stopPhoto, command=stopMusic)
    stopBtn.grid(row=0, column=1, padx=10, ipady=5, ipadx=5)

    # pause button
    pausePhoto = PhotoImage(file=r'assets/pause.png')
    pauseBtn = ttk.Button(middleFrame, image=pausePhoto, command=pauseMusic)
    pauseBtn.grid(row=0, column=2, padx=10, ipady=5, ipadx=5)

    middleFrame.pack(pady=30, padx=30)

    # bottom frame for forward, rewind, mute/unmute and volume
    bottomFrame = Frame(rightFrame, bg="#ECECEC")
    bottomFrame.pack(padx=30)

    # rewind button
    rewindPhoto = PhotoImage(file=r'assets/rewind.png')
    rewindBtn = ttk.Button(bottomFrame, image=rewindPhoto, command=lambda: rewindMusic(playList, playListBox))
    rewindBtn.grid(row=0, column=0, ipady=3, ipadx=3)

    # forward button
    forwardPhoto = PhotoImage(file=r'assets/forward.png')
    rewindBtn = ttk.Button(bottomFrame, image=forwardPhoto, command=lambda: forwardMusic(playList, playListBox))
    rewindBtn.grid(row=0, column=1, ipady=3, ipadx=3)

    # mute/unmute button
    mutePhoto = PhotoImage(file=r'assets/mute.png')
    unmutePhoto = PhotoImage(file=r'assets/unmute.png')
    volumeBtn = ttk.Button(bottomFrame, image=unmutePhoto, command=muteMusic)
    volumeBtn.grid(row=0, column=2, ipady=3, ipadx=3)

    # volume scale
    scale = ttk.Scale(bottomFrame, from_=0, to=100, orient=HORIZONTAL, command=setVolume)
    scale.set(DEFAULT_VOLUME)  # implement the default value of scale when music player starts
    mixer.music.set_volume(DEFAULT_VOLUME/10)
    scale.grid(row=0, column=3, pady=15, padx=15, ipady=3, ipadx=3)

    # custom event handler upon exiting Melody
    root.protocol("WM_DELETE_WINDOW", exitWindow)

    root.mainloop()
