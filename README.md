# Spotify-ML-Music-Recommendations
Music recommendations based on your favorite artists, songs, and listening history powered by machine learning

In order to run this program, you will have to create a spotify developer account and enter your client credentials and
spotify username in the code.

Create a Spotify Developer account here: https://developer.spotify.com/dashboard/login

# How it Works 
By entering your favorite artist and favorite songs from that artist, this program recommends you songs from that artist that are similar to your favorite songs in terms of their audio features (see files `DrakeTrackData.csv` and `DrakeTrackDataClustered` as examples). 

This recommendation system is done through k-means clustering, which groups each song into a cluster, where all songs in the same cluster have similar audio features. 

The program also goes through your Spotify listening history and finds other artists and songs you frequently listen to and recommends you similar songs from those artists with the same recommendation system. 
