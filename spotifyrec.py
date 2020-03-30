
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import spotipy.util as util
import sys 
import requests

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from itertools import chain 
  

token = ''
sp = ''

trackData = []
df = []
artists = []
tracks = []
trackData = []
savedURIs = []

artistTrackURIs = []
artistTrackData = []
albumNames = []
albumUris = []

spotifyAlbums = {}
albumCount = 0


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

    client_id = '2db982c8b2f54c2ca27196012512659a'
    client_secret = 'd26051b027314cf1aace14b3046b36a7'

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id,
                                                        client_secret=client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


    username = 'xfaizy'
    redirect_uri = 'https://google.com'
    scope = 'user-library-read'


    token = util.prompt_for_user_token(username=username, 
                                    scope=scope, 
                                    client_id=client_id,   
                                    client_secret=client_secret,     
                                    redirect_uri=redirect_uri)


def getTrackData():

    global trackData
    global df

    sp = spotipy.Spotify(auth=token)
    counter = 0

    for x in range(10):
        
        try:

            results = sp.current_user_saved_tracks(limit=50, offset=counter)

            for item in results['items']:

                track = item['track']
                trackName = fixString(track['name'])
                artist = fixString(track['artists'][0]['name'])

                trackData.append([trackName, artist])
                counter += 1
        
        except:

            print('Error')
            

    df = pd.DataFrame(trackData, columns = ['Track', 'Artist']) 


def getSpotifyURIs(df):
    
    global savedURIs

    artistNames = df['Artist'].values
    trackNames = df['Track'].values
    
    for x in range(len(artistNames)):
        
        artist = fixString(artistNames[x])
        track = fixString(trackNames[x])

        q = 'artist:{} track: {}'.format(artist, track)
        results = sp.search(q=q, limit=1, type='track')
        
        try:
            uri = results['tracks']['items'][0]['uri']
            savedURIs.append(uri)
        
        except:
            print(x, artist, track + '\n')


    return savedURIs


def getAudioFeatures(savedURIs, artistName):
    
    global sp

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
    
    counter = 0
    iterations = len(savedURIs) 

    print('Analyzing data for ' + str(iterations) + ' tracks')

    for uri in savedURIs:
        
        x = sp.audio_features(uri)
        y = sp.track(uri)

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
    df['uris'] = savedURIs

    
    if artist == 'general':
        df.to_csv('C:\\Users\\faiza\\OneDrive\\Desktop\\SpotifyData.csv')

    else:
        df.to_csv('C:\\Users\\faiza\\OneDrive\\Desktop\\' + artistName.replace(' ', '') + 'TrackData.csv')

    print('\nDone!')

    return df


def clusterData(fileName):

    dataset = pd.read_csv('C:\\Users\\faiza\\OneDrive\\Desktop\\' + fileName.replace(' ', '') + '.csv')

    x = dataset.iloc[:, [3,4,5,6,7,8,9,10,11,12,13,14]].values

    clusters = elbowMethod(x)
    kmeans = KMeans(n_clusters = clusters)
    y_kmeans = kmeans.fit_predict(x)

    print('\nNumber of Clusters:', clusters)

    data = dataset.values.tolist()
    exportData = []

    for x in range(len(data)):
        
        #print(data[x][1], data[x][2], y_kmeans[x])
        exportData.append([data[x][-1], data[x][1], data[x][2], y_kmeans[x]])


    MyFile = open('C:\\Users\\faiza\\OneDrive\\Desktop\\' + fileName.replace(' ', '') + 'Clustered.csv','w')

    header = 'URI, Artist,Song,Cluster' + '\n'

    MyFile.write(header)

    for row in exportData:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()

    print('\nSaved as ' + fileName.replace(' ', '') + 'Clustered.csv')


def albumSongs(uri):
    
    global artistTrackURIs

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
        
        spotifyAlbums[album]['album'].append(albumNames[albumCount]) #append album name tracked via album_count
        spotifyAlbums[album]['track_number'].append(tracks['items'][n]['track_number'])
        spotifyAlbums[album]['id'].append(tracks['items'][n]['id'])
        spotifyAlbums[album]['name'].append(tracks['items'][n]['name'])
        spotifyAlbums[album]['uri'].append(tracks['items'][n]['uri'])
        
        trackURI = tracks['items'][n]['uri']

        if trackURI not in artistTrackURIs:
            artistTrackURIs.append(trackURI)

        
def getArtistTracks(artistName):

    global artistTrackURIs
    global albumNames
    global albumUris
    global albumCount

    result = sp.search(artistName) #search query

    spotifyArtistName = result['tracks']['items'][0]['artists'][0]['name']
    artistUri = result['tracks']['items'][0]['artists'][0]['uri']

    if spotifyArtistName.casefold() != artistName.casefold():
        artistUri = result['tracks']['items'][0]['artists'][1]['uri']
    
    
    print(artistName, artistUri)

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
    
        albumSongs(i)
        albumCount += 1 


def recommendSongs(artist, favSongs):

    df = pd.read_csv('C:\\Users\\faiza\\OneDrive\\Desktop\\' + artist.replace(' ', '') + 'TrackDataClustered.csv', encoding = "latin-1")
    data = df.values.tolist()

    favSongClusters = []
    clusters = []
    recSongs = []
    index = 0

    for x in range(len(data)):
        
        trackName = data[x][2].lower()
        cluster = data[x][3]

        for song in favSongs:
            
            if clean(song.lower()) in clean(trackName):
                
                if cluster not in clusters:
                    clusters.append(cluster)
                
                favSongClusters.append([song, cluster])


    for x in range(len(data)):
        
        trackName = data[x][2]
        cluster = data[x][3]

        if cluster in clusters:
            recSongs.append([trackName[1:], cluster])


    print('\n\nRecommended Songs for ' + artist + ':\n')

    for x in range(len(favSongClusters)):
        
        print('\nBecause you like ' + favSongClusters[x][0] + ':\n')
        
        for y in range(len(recSongs)):
            
            songName = recSongs[y][0]
            songCluster = recSongs[y][1]

            if favSongClusters[x][0].casefold() not in songName.casefold() and favSongClusters[x][1] == songCluster:
                print(recSongs[y][0])

    
    print('\nTotal Songs:', len(recSongs))




initialize()

'''
getTrackData()

getSpotifyURIs(df)

getAudioFeatures(savedURIs)
'''

#clusterData('general')


artist = "A boogie wit da hoodie"

favSongs = ['no promises', 'just like me']


getArtistTracks(artist)

getAudioFeatures(artistTrackURIs, artist)

clusterData(artist + 'TrackData')


recommendSongs(artist, favSongs)
