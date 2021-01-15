
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import spotipy.util as util
import sys 
import requests

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from itertools import chain 
import random
import os
  

username = 'xfaizy'
client_id = '2db982c8b2f54c2ca27196012512659a'
client_secret = 'd26051b027314cf1aace14b3046b36a7'


token = ''
sp = ''

userSavedSongURIs = []
userSavedSongNames = []

trackData = []
df = []
artists = []
tracks = []
trackData = []

originalArtist = ''
artistTrackURIs = []
artistSongs = []
albumNames = []
albumUris = []
topArtists = []
result = []
outputSongs = []

recSongURIs = []
spotifyAlbums = {}


scope = 'user-top-read'


def clean(stng):
    
    output = ''

    for letter in stng:
        if letter != '[' and letter != ']' and letter != "'": #and letter != ' ':
            output += letter
        
    return output


def fixString(stng):
   
    output = ''

    for x in range(len(stng)):
        if stng[x] != "'" and stng[x] != ',':
            output += stng[x]

    return output


def elbowMethod(x):

    error = []

    for i in range(1, 11):
        
        kmeans = KMeans(n_clusters = i).fit(x)
        kmeans.fit(x)
        error.append(kmeans.inertia_)

    '''    
    plt.plot(range(1, 11), Error)
    plt.title('Elbow method')
    plt.xlabel('No of clusters')
    plt.ylabel('Error')
    plt.show()
    '''

    minimum = min(error)
    return error.index(minimum)


def progress(count, total, status=''):
    
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def initialize():

    global token
    global sp
    global username
    global scope
    global client_id
    global client_secret


    client_credentials_manager = SpotifyClientCredentials(client_id=client_id,
                                                        client_secret=client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


    redirect_uri = 'https://google.com'


    token = util.prompt_for_user_token(username=username, 
                                    scope=scope, 
                                    client_id=client_id,   
                                    client_secret=client_secret,     
                                    redirect_uri=redirect_uri)
        

def getUserSavedSongsData():

    global trackData
    global df
    global userSavedSongNames

    sp = spotipy.Spotify(auth=token)
    counter = 0

    print('\nAnalyzing your saved songs...')

    for x in range(20):
        
        try:

            results = sp.current_user_saved_tracks(limit=50, offset=counter)

            for item in results['items']:

                track = item['track']
                trackName = fixString(track['name'])
                artist = fixString(track['artists'][0]['name'])

                trackData.append([trackName, artist])
                counter += 1

        except:

            counter += 0
            

    df = pd.DataFrame(trackData, columns = ['Track', 'Artist']) 

    artistNames = df['Artist'].values
    trackNames = df['Track'].values

    userSavedSongs = list(trackNames)

    for x in range(len(artistNames)):
        
        artist = fixString(artistNames[x])
        track = fixString(trackNames[x])

        userSavedSongNames.append(track)

        q = 'artist:{} track: {}'.format(artist, track)
        results = sp.search(q=q, limit=1, type='track')
        
        try:
            uri = results['tracks']['items'][0]['uri']
            userSavedSongURIs.append(uri)
        
        except:
            #print(x, artist, track + '\n')
            print()

    
def getAudioFeatures(savedURIs, artistName):
    
    global sp
    global rawArtistName

    artist = []
    track = []
    
    danceability = []
    energy = []
    key = []
    loudness = []
    mode = []
    speechiness = []
    acousticness = []
    instrumentalness = []
    liveness = []
    valence = []
    tempo = []
    duration_ms = []
    updatedURIs = []
    
    counter = 0
    iterations = len(savedURIs) 

    print('\nExtracting audio data from ' + str(iterations) + ' tracks...')

    for uri in savedURIs:
        
        x = sp.audio_features(uri)
        y = sp.track(uri)

        aud = [audio_features for audio_features in x]

        if None not in aud:

            for audio_features in x:

                danceability.append(audio_features['danceability'])
                energy.append(audio_features['energy'])
                key.append(audio_features['key'])
                loudness.append(audio_features['loudness'])
                mode.append(audio_features['mode'])
                speechiness.append(audio_features['speechiness'])
                acousticness.append(audio_features['acousticness'])
                instrumentalness.append(audio_features['instrumentalness'])
                liveness.append(audio_features['liveness'])
                valence.append(audio_features['valence'])
                tempo.append(audio_features['tempo'])
                duration_ms.append(audio_features['duration_ms'])
 
            artist.append(fixString(y['album']['artists'][0]['name']))
            track.append(fixString(y['name']))
            updatedURIs.append(uri)


        progress(counter, iterations, status='Loading...')
        counter += 1


    df = pd.DataFrame()
    df['artist'] = artist
    df['track'] = track
    df['danceability'] = danceability
    df['energy'] = energy
    df['key'] = key
    df['loudness'] = loudness
    df['mode'] = mode
    df['speechiness'] = speechiness
    df['acousticness'] = acousticness
    df['instrumentalness'] = instrumentalness
    df['liveness'] = liveness
    df['valence'] = valence
    df['tempo'] = tempo
    df['duration_ms'] = duration_ms
    df['uris'] = updatedURIs

    
    if artistName == 'general':
        df.to_csv(fileName + 'SpotifyData.csv')
        print('\nSaved as ' + fileName + 'SpotifyData.csv')

    elif artistName == 'recSongs':
        df.to_csv(recSongFileName)
        print('\nSaved as ' + recSongFileName)

    else:
        df.to_csv(fileName + 'TrackData.csv')
        print('\nSaved as ' + fileName + 'TrackData.csv')

    return df


def clusterData(fileName, artist):

    dataset = pd.read_csv(fileName + 'TrackData.csv')
    saveAs = fileName + 'TrackDataClustered.csv'
    addedClusters = 1

    if artist == 'general':
        dataset = pd.read_csv(fileName + 'SpotifyData.csv')
    
    if artist == 'recSongs':
        dataset = pd.read_csv(recSongFileName)
        saveAs = recSongFileName[:-4] + 'Clustered.csv'
        addedClusters = int(len(dataset) / 23)

    x = dataset.iloc[:, [3,4,5,6,7,8,9,10,11,12,13,14]].values

    clusters = elbowMethod(x) + addedClusters
    kmeans = KMeans(n_clusters = clusters)
    y_kmeans = kmeans.fit_predict(x)

    print('\nClustering tracks...')
    print('\nNumber of Clusters:', clusters)

    data = dataset.values.tolist()
    exportData = []


    for x in range(len(data)):
        
        exportData.append([data[x][-1], data[x][1], data[x][2], y_kmeans[x]])


    MyFile = open(saveAs, 'w')

    header = 'URI, Artist,Song,Cluster' + '\n'

    MyFile.write(header)

    for row in exportData:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()

    print('\nSaved as ' + saveAs)


def checkIfArtistValid(artist):
    
    global result

    try:
        result = sp.search(artist)
        spotifyArtistName = result['tracks']['items'][0]['artists'][0]['name']
        artistUri = result['tracks']['items'][0]['artists'][0]['uri']
        
        return True
    except:
        return False


def checkIfSongValid(userFavSongs, artistSongs):

    match = False

    for song in artistSongs:
        
        for userFavSong in userFavSongs:
            if userFavSong.lower() in song:
                match = True

    return match


def albumSongs(uri, multiple):
    
    global artistTrackURIs
    global recSongURIs 

    album = uri #assign album uri to a_name
    spotifyAlbums[album] = {} #Creates dictionary for that specific album

    #Create keys-values of empty lists inside nested dictionary for album

    spotifyAlbums[album]['album'] = [] #create empty list
    spotifyAlbums[album]['track_number'] = []
    spotifyAlbums[album]['id'] = []
    spotifyAlbums[album]['name'] = []
    spotifyAlbums[album]['uri'] = []

    tracks = sp.album_tracks(album) #pull data on album tracks
    
    for n in range(len(tracks['items'])): #for each song track
        
        #spotifyAlbums[album]['album'].append(albumNames[albumCount]) #append album name tracked via album_count
        spotifyAlbums[album]['track_number'].append(tracks['items'][n]['track_number'])
        spotifyAlbums[album]['id'].append(tracks['items'][n]['id'])
        spotifyAlbums[album]['name'].append(tracks['items'][n]['name'])
        spotifyAlbums[album]['uri'].append(tracks['items'][n]['uri'])
        
        trackURI = tracks['items'][n]['uri']

        if multiple == False and trackURI not in artistTrackURIs:
            artistTrackURIs.append(trackURI)
            artistSongs.append((tracks['items'][n]['name']).lower())
        
        if multiple == True and trackURI not in recSongURIs:
            recSongURIs.append(trackURI)

        
def getArtistTracks(artists):

    global artistTrackURIs
    global albumNames
    global albumUris
    global artist
    global favSongs
    global result

    multiple = True

    if len(artists) == 1:
        multiple = False

    for artist in artists:  
            
        validArtist = checkIfArtistValid(artist)

        while validArtist == False:
        
            print('\nArtist not found, try again: ')
            artist = input("\nEnter artist: ") 
            validArtist = checkIfArtistValid(artist)

        spotifyArtistName = result['tracks']['items'][0]['artists'][0]['name']
        artistUri = result['tracks']['items'][0]['artists'][0]['uri']

        #print(spotifyArtistName, artistUri)
        #print(result['tracks']['items'][1]['artists'][0]['uri'])

        if spotifyArtistName.casefold() != artist.casefold():
            
            try:
                artistUri = result['tracks']['items'][0]['artists'][1]['uri']
            except:
                artistUri = result['tracks']['items'][1]['artists'][0]['uri']
                #print(spotifyArtistName, artist)
                #print(result)

        invalidArtist = False

        if multiple == False:
            print('\n' + artist, artistUri)

        #Pull all of the artist's albums
        spAlbums = sp.artist_albums(artistUri, album_type='album')


        #Store artist's albums' names' and uris in separate lists
        for i in range(len(spAlbums['items'])):
            
            albumNames.append(spAlbums['items'][i]['name'])
            albumUris.append(spAlbums['items'][i]['uri'])


        noDuplicateAlbumURIs = [] 
        noDuplicateAlbumNames = []


        for x in range(len(albumUris)):

            if albumNames[x] not in noDuplicateAlbumNames:

                noDuplicateAlbumURIs.append(albumUris[x])
                noDuplicateAlbumNames.append(albumNames[x])

        for i in noDuplicateAlbumURIs:
        
            albumSongs(i, multiple)


        validSong = checkIfSongValid(favSongs, artistSongs)

        while validSong == False:
            
            print('\nSong invalid, try again')
            rawFavSongs = input("Enter favorite songs from that artist separated by commas: ") 
            favSongs = [x.strip() for x in rawFavSongs.split(',')]
    
            validSong = checkIfSongValid(favSongs, artistSongs)


def recommendSongs(artistName, favSongs):

    global topArtists
    global artist
    global userSavedSongNames
    global outputSongs

    openFile = fileName + 'TrackDataClustered.csv'

    if artistName == 'recSongs':
        openFile = recSongFileName[:-4] + 'Clustered.csv'

    df = pd.read_csv(openFile, encoding = "latin-1")
    data = df.values.tolist()

    favSongClusters = []
    clusters = []
    recSongs = []
    index = 0
    counter = 0

    favSongsLowercase = [song.lower() for song in favSongs]

    for x in range(len(data)):
        
        trackName = data[x][2].lower()
        cluster = data[x][3]

        for song in favSongs:
            
            if (clean(song.lower()) in clean(trackName)) or (artistName == 'recSongs' and clean(song.lower())[song.find(' ') + 1 : ] in clean(trackName)):
                
                if cluster not in clusters:
                    clusters.append(cluster)
                
                favSongClusters.append([song, cluster])


    for x in range(len(data)):
        
        atName = data[x][1]
        trackName = data[x][2]
        cluster = data[x][3]

        if cluster in clusters:
            recSongs.append([trackName[1:], cluster, atName, data[x][0]])


    if artistName != 'recSongs':
        print('Cluster #s', clusters)
        print('\n\nRecommended Songs for ' + artistName + ':\n')
    else:
        print('\n\nRecommended songs based on your listening history:' + '\n')


    for x in range(len(favSongClusters)):
        
        if artistName != 'recSongs' and len(favSongs) != 1 and len(clusters) != 1:
            print('\nBecause you like ' + favSongClusters[x][0] + ':\n')
        
        for y in range(len(recSongs)):
            
            songName = recSongs[y][0]
            songCluster = recSongs[y][1]
            recSongArtistName = recSongs[y][2][1:]
            
            userFavSong = favSongClusters[x][0]
            userFavSongCluster = favSongClusters[x][1]

            if songName.lower() not in favSongsLowercase and userFavSong.casefold() not in songName.casefold() and userFavSongCluster == songCluster and songName not in outputSongs and recSongs[y][3] not in userSavedSongURIs and songName not in userSavedSongNames:
                
                if artistName == 'recSongs' and recSongArtistName.casefold() != originalArtist.casefold(): 
                    print(recSongArtistName, songName)
                    outputSongs.append(songName)
                    counter += 1

                elif artistName != 'recSongs':
                    print(songName)
                    outputSongs.append(songName)
                    counter += 1
    
    print('\nTotal Songs:', counter)


def recommendOtherArtistSongs():

    global username
    global scope 
    global fileName
    global topArtists

    term = random.randint(0, 2)
    numSongs = random.randint(5, 15)

    timeRange = 'short_term'

    if term == 1:
        timeRange = 'medium_term'
    elif term == 2:
        timeRange = 'long_term'

    token = util.prompt_for_user_token(username, scope)
    topSongs = []

    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=numSongs, time_range=timeRange)

    #print('\nTop Tracks\n')

    for x in range(numSongs):
        
        artistName = fixString(results['items'][x]['artists'][0]['name'])
        songName = results['items'][x]['name']
        
        topArtists.append(artistName)
        topSongs.append(artistName + ' ' + songName)
        #print(artistName, songName)


    print('\n\nAnalyzing your listening history...')
    getArtistTracks(topArtists)
    getAudioFeatures(recSongURIs, 'recSongs')
    clusterData(fileName, 'recSongs')
    recommendSongs('recSongs', topSongs)



if os.path.isdir('SongData') == False:

    # Creating the SongData Folder
    songDataDir = "SongData"
    parentDir = os.getcwd()
    songDataPath = os.path.join(parentDir, songDataDir) 
    os.mkdir(songDataPath) 


path = 'SongData\\'

initialize()

artist = input("\nEnter artist: ") 
originalArtist = artist

rawFavSongs = input("Enter favorite songs from that artist separated by commas: ") 
favSongs = [x.strip() for x in rawFavSongs.split(',')]

rawArtistName = artist.replace(' ', '')

fileName = path + rawArtistName
recSongFileName = path + 'SpotifyRecSongData.csv'

getArtistTracks([artist])

getAudioFeatures(artistTrackURIs, artist)

clusterData(fileName, artist)

getUserSavedSongsData()

recommendSongs(artist, favSongs)

recommendOtherArtistSongs()


