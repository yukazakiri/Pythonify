import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from ytmusicapi import YTMusic
import os
import sys
import subprocess

# Spotify API credentials
CLIENT_ID = '{Your Spotify Client ID}'
CLIENT_SECRET = '{Your Spotify Client Secret}'

# Initialize clients
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
ytmusic = YTMusic()

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        if sys.platform.startswith('win'):
            return os.path.join(sys._MEIPASS, 'ffmpeg.exe')
        else:
            return 'ffmpeg'
    else:
        return 'ffmpeg'

def check_ffmpeg():
    ffmpeg_path = get_ffmpeg_path()
    try:
        subprocess.run([ffmpeg_path, '-version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg is not installed or not accessible.")
        return False

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
            'ffmpeg_location': get_ffmpeg_path(),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return os.path.exists(f"{output_template}.mp3")
    except Exception as e:
        print(f"Error downloading track: {str(e)}")
        return False

def main():
    if not check_ffmpeg():
        print("Please install FFmpeg and make sure it's in your system PATH")
        return

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
