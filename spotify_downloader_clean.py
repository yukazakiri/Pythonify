import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from ytmusicapi import YTMusic
import os

# Spotify API credentials
CLIENT_ID = '471d9253fa4b4deb82ffaddc8c7d3510'
CLIENT_SECRET = 'bb608567541a4adf857d0e87a2c1b5f1'

# Initialize clients
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
ytmusic = YTMusic()

def get_track_info(track_url):
    try:
        track_id = track_url.split('/')[-1].split('?')[0]
        track = sp.track(track_id)
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name']
        }
    except:
        return None

def get_playlist_tracks(playlist_url):
    try:
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        results = sp.playlist_tracks(playlist_id)
        tracks = []
        for item in results['items']:
            track = item['track']
            tracks.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name']
            })
        return tracks
    except:
        return None

def download_track(track_info):
    query = f"{track_info['name']} {track_info['artist']}"
    output_template = f"{track_info['name']} - {track_info['artist']}"

    try:
        search_results = ytmusic.search(query, filter="songs", limit=1)
        if not search_results:
            return False

        video_id = search_results[0]['videoId']
        video_url = f"https://music.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f"{output_template}.%(ext)s",
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return os.path.exists(f"{output_template}.mp3")
    except:
        return False

def main():
    url = input("Enter the Spotify track or playlist URL: ")
    
    if 'playlist' in url:
        tracks = get_playlist_tracks(url)
        if not tracks:
            print("Failed to get playlist information.")
            return
        
        print(f"Found {len(tracks)} tracks in the playlist.")
        for i, track_info in enumerate(tracks, 1):
            print(f"Downloading track {i}/{len(tracks)}: {track_info['name']} by {track_info['artist']}")
            if download_track(track_info):
                print(f"Successfully downloaded: {track_info['name']} by {track_info['artist']}")
            else:
                print(f"Failed to download: {track_info['name']} by {track_info['artist']}")
    else:
        track_info = get_track_info(url)
        if not track_info:
            print("Failed to get track information.")
            return

        if download_track(track_info):
            print(f"Successfully downloaded: {track_info['name']} by {track_info['artist']}")
        else:
            print("Failed to download the track.")

if __name__ == "__main__":
    main()
