import json
from tkinter import *
import os.path
import os
import sys
import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyOAuth  # Auth
from spotipy.oauth2 import SpotifyClientCredentials  # auth
# import pandas as pd
# import time
playlists = []  # dict, name is key, value is songs
genresOverall = {}  # key is genre and value is number

# read my credentials from my-credentials to start the spotipy
try:
    f = open("my-credentials.txt", "r")
    credentials = f.read()
    id = credentials.split(",")[0]
    secret = credentials.split(",")[1]
    f.close()

    auth_manager = SpotifyClientCredentials(client_id=id, client_secret=secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
except IndexError as index:
    print("Credentials not present. \nPlease include Client Id and Client Secret in a comma-separated string in a text file.")
    f.close()
    sys.exit()
except FileNotFoundError as file_not_found:
    print(file_not_found.filename, "not found")
    f.close()
    sys.exit()


def askCreds():
    haveCreds = input("Do you have Spotify api credentials? (Y/N): ")
    if haveCreds == "Y":
        id = input("Enter your CLIENT ID: ")
        secret = input("Enter your CLIENT SECRET: ")
        auth_manager = SpotifyClientCredentials(
            client_id=id, client_secret=secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)


# ==================Classes=====================
class Song:
    def __init__(self, artists, name, uri):
        self.name = name
        self.artists = artists
        self.uri = uri


class Playlist:
    def __init__(self, name, genres, songs, size):
        self.name = name
        self.size = size
        self.genres = genres
        self.songs = songs


class Artist:
    def __init__(self, name, genres):
        self.name = name
        self.genres = genres

# get data and make list of Playlists


# ==================Helping Functions (Getters)=====================
"""acousticness — how acoustic
danceability — self-explanatory
energy — how 'fast, loud an noisy'
instrumentalness — the less vocals, the higher
liveness — whether there is audience in the recording
loudness — self-explanatory
speechiness — the more spoken words, the higher
valence — whether the track sounds happy or sad
tempo — the bpm"""


def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def getSongName(uri):
    return sp.track(uri)['name']


def getDanceability(uri):
    features = sp.audio_features(uri)
    return features[0]['danceability']


def getAcousticness(uri):
    features = sp.audio_features(uri)
    return features[0]['acousticness']


def getTempo(uri):
    features = sp.audio_features(uri)
    return features[0]['tempo']


def getValence(uri):
    features = sp.audio_features(uri)
    return features[0]['valence']


def getEnergy(uri):
    features = sp.audio_features(uri)
    return features[0]['energy']


def getSpeechiness(uri):
    features = sp.audio_features(uri)
    return features[0]['speechiness']

# ==================Main Functions=====================


def searchforPl(arr, low, high, x):
    # Check base case
    if high >= low:

        mid = (high + low) // 2

        # If element is present at the middle itself
        if arr[mid].name == x:
            return mid

        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif arr[mid].name > x:
            return searchforPl(arr, low, mid - 1, x)

        # Else the element can only be present in right subarray
        else:
            return searchforPl(arr, mid + 1, high, x)

    else:
        # Element is not present in the array
        return -1


def extractData():
    tracklist = []
    # get my data from my json file

    with open('Playlist1.json', encoding="utf-8") as f:
        data = json.load(f)

    songList = []

    # generate a percentage of genres in a pl
    totalGenreCnt = 0
    percentGenre = 0
    playlistsDict = {}
    playlistsDict['myPlaylists'] = []
    topGenres = {}
    thisGenres = {}
    uriList = []
    # print()
    # go thru playlists
    for playlist in data['playlists']:
        # create a playlist object containing just a name
        playlistObj = Playlist(playlist['name'], {}, [], 0)
        print("-----")
        # go thru songs in playlist
        for item in playlist['items']:
            # if there is a track, make a song object and append to songs list in playlist obj
            if(item['track'] is not None):
                # print(item['track']['trackName'])
                song = Song(item['track']['artistName'], item['track']
                            ['trackName'], item['track']['trackUri'])

                # append song as a dictionary to songs list in playlist
                playlistObj.songs.append(song.__dict__)

                # extract uri to get song info
                uris = song.uri.split(":")
                track_info = sp.track(uris[2])
                # returns list of artists with info
                artists_on_track = track_info['artists']
                # go thru singers on track
                for singer in artists_on_track:
                    # print(singer)
                    artist_info = singer['uri']
                    artist = sp.artist(artist_info)
                    for genre in artist['genres']:
                        # print(genre, " found")
                        if genre in thisGenres:
                            thisGenres[genre] += 1
                        else:
                            thisGenres[genre] = 1

                        if genre in genresOverall:
                            genresOverall[genre] += 1
                        else:
                            genresOverall[genre] = 1
        # a genre should appear about 15% of the time to be considered substantial
        playlistObj.size = len(playlistObj.songs)
        for key, value in thisGenres.items():
            if playlistObj.size <= 20:  # small playlists have at most 3
                if value >= 3:
                   # print("value: ", value)
                    playlistObj.genres[key] = value
                    totalGenreCnt += value
                   # print("total: ", totalGenreCnt)
            elif playlistObj.size <= 30:  # 21-30 songs genres reappear 5ish times
                if value >= 5:
                   # print("value: ", value)
                    playlistObj.genres[key] = value
                    totalGenreCnt += value
                   # print("total: ", totalGenreCnt)
            elif playlistObj.size <= 40:  # medium playlists
                if value >= 7:
                   # print("value: ", value)
                    playlistObj.genres[key] = value
                    totalGenreCnt += value
                   # print("total: ", totalGenreCnt)
            elif playlistObj.size <= 50:  # large playlists
                if value >= 10:
                   # print("value: ", value)
                    playlistObj.genres[key] = value
                    totalGenreCnt += value
                   # print("total: ", totalGenreCnt)
            elif playlistObj.size > 50:  # extra large playlists
                if value >= 15:
                   # print("value: ", value)
                    playlistObj.genres[key] = value
                    totalGenreCnt += value
                    # print("total: ", totalGenreCnt)

        playlists.append(playlistObj)
        thisGenres.clear()
        totalGenreCnt = 0
        topGenres.clear()
        songList.clear()
        # print("\tfinal size: ", len(playlistObj.genres))
        # print("\tsongs size: ", len(playlistObj.songs))
        playlistsDict['myPlaylists'].append(playlistObj.__dict__)

    playlists.sort(key=lambda x: x.name)
    for pl in playlists:
        print("----", pl.name, "----")

    # go thru each song in each playlist and get artists of songs and then get the gernes and add it to playlist
    # for key, value in playlists.items():
    """
    for pl in playlists:
        print(pl.name)
        for song in pl.songs:
            uris = song.uri.split(":")
            track_info = sp.track(uris[2])
            # returns list of artists with info
            artists_on_track = track_info['artists']
            for singer in artists_on_track:
                # print(singer)
                artist_info = singer['uri']
                artist = sp.artist(artist_info)
                for genre in artist['genres']:
                    # print(genre, " found")
                    if genre in pl.genres:
                        pl.genres[genre] += 1
                    else:
                        pl.genres[genre] = 1

                    if genre in genresOverall:
                        genresOverall[genre] += 1
                    else:
                        genresOverall[genre] = 1
                        # name is just a string and genres is a list
        for key, value in pl.genres.items():
            if(value > 10):
                topGenres[key] = value
        pl.genres = topGenres
        playlistsDict['myPlaylists'].append(pl.__dict__)"""

    with open("cleaned-data.json", "w") as writeFile:
        json.dump(playlistsDict, writeFile)
    print("Done writing")


def analyzePl(name):
    # get overall danceability --type of audience
    # get loudness -- chillness factor
    # get valence -- happy or sad
    # get energy -- setting
    # get tempo --
    songList = []
    plGenres = []
    totalEnergy = 0
    totalValence = 0
    totalSpeechiness = 0
    plSize = 0
    # found = False
    index = searchforPl(playlists, 0, len(playlists), name)
    """
    for pl in playlists:
        if pl.name == name:
            found = True
            songList = pl.songs
            plSize = pl.size
            sortedG = sorted(pl.genres.items(),
                             key=lambda x: x[1], reverse=True)
            for g in sortedG:
                plGenres.append(g[0])
            break
        """

    # "{:.2f}".format(float)
    if index != -1:
        songList = playlists[index].songs
        plSize = playlists[index].size
        sortedG = sorted(playlists[index].genres.items(),
                         key=lambda x: x[1], reverse=True)
        for g in sortedG:
            plGenres.append(g[0])

        for song in songList:
            uri = song['uri']
            totalEnergy += getEnergy(uri)
            totalValence += getValence(uri)
            totalSpeechiness += getSpeechiness(uri)
        avgEnergy = totalEnergy/plSize
        avgValence = totalValence/plSize
        avgSpeechines = totalSpeechiness/plSize
        for i in range(len(plGenres)):
            print(i, ".", plGenres[i])

        print("Avg Energy:", "{:.2f}".format(avgEnergy), "\nAvg Valence:",
              "{:.2f}".format(avgValence), "\nAvg Speechiness", "{:.2f}".format(avgSpeechines))
    else:
        print("Playlist not found")


def getSongGenres(uri):
    track_info = sp.track(uri)
    # returns list of artists with info
    artists_on_track = track_info['artists']
    # go thru singers on track
    if(len(artists_on_track) > 0):
        genres = sp.artist(artists_on_track[0]['uri'])['genres']
    return genres


def analyzeSong(uri):

    danceability = getDanceability(uri)

    valence = getValence(uri)
    energy = getEnergy(uri)
    tempo = getTempo(uri)
    speechiness = getSpeechiness(uri)
    track_name = getSongName(uri)
    print(track_name, "has the following:\nDanceability:", danceability,
          "\nValence", valence, "\nEnergy", energy, "\nTempo", tempo, "\nSpeechiness", speechiness)
    # print(features[0]['danceability'])


def getMostPlayedGenre():
    print("ok now to most played")
    numPlays = 1
    mostPlayed = []
    mostPlayedStr = ""

    for i in sorted(genresOverall.values()):
        print(numPlays, ": ", i)
        numPlays += 1
        if(numPlays == 10):
            break
    """for key, value in genresOverall.items():
        if value > numPlays:
            numPlays = value
            mostPlayed = list(key)"""


# Tkinter sample code for future GUI
"""window = Tk()
# giving title to the main window
window.title("First_Program")
window.geometry('100x100')
btn = Button(window, text="print", command=hello).pack(side='top')
# Label is what output will be
# show on the window
# label = Label(window, text="Hello World !").pack()

# calling mainloop method which is used
# when your application is ready to run
# and it tells the code to keep displaying
window.mainloop()"""
# ================== MENU =====================
opt = -1
while(opt != 5):
    print("Welcome to your playlist analyzer")
    print(" 1. extractData \n 2. analyzePl \n 3. analyzeSong \n 4. showSongGenres \n 5. Quit")
    opt = int(input("> "))
    if opt == 1:
        extractData()
        clearConsole()
    elif opt == 2:
        plName = input("Enter playlist name:")
        analyzePl(plName)
    elif opt == 3:
        uri = input("Enter Uri:")
        analyzeSong(uri)
    elif opt == 4:
        uri = input("Enter Uri:")
        print(getSongGenres(uri))
