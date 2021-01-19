# Spotify-ML-Music-Recommendations
Music recommendations based on your favorite artists, songs, and listening history powered by machine learning!

# How it Works 
By entering your favorite artist and favorite songs from that artist, this program recommends you songs from that artist that are similar to your favorite songs in terms of their audio features (see files `DrakeTrackData.csv` and `DrakeTrackDataClustered` as examples). 

This recommendation system is done through k-means clustering, which groups each song into a cluster in which all songs in the same cluster have similar audio features. Given that I like songs with similar beats and rhythms, I thought this would be an effective way to find new, catchy music to listen to. 

The program also goes through your Spotify listening history and finds other artists and songs you frequently listen to and recommends you similar songs from those artists with the same recommendation system. 

# How to Run the Code

  - If you do not have **git** installed, download it [here](https://git-scm.com/downloads)
  - If you do not have **pip** installed, download it [here](https://pip.pypa.io/en/stable/installing/)
  
  - Clone the repository `git clone https://github.com/faizancodes/Spotify-ML-Music-Recommendations.git`
  
  - Navigate to the downloaded folder `cd Spotify-ML-Music-Recommendations`
  
  - Download all the dependencies `pip install -r requirements.txt` 
  
  - Create a Spotify Developer account [here](https://developer.spotify.com/dashboard/login)
      - Enter your client credentials and spotify username in the `spotifyrec.py` file
      
  - Run `spotifyrec.py` to execute the code
