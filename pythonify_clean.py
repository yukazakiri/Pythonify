import os
import sys
import subprocess
import requests
import zipfile
import shutil
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from ytmusicapi import YTMusic
from shutil import which

# Load environment variables
load_dotenv()

# Spotify API credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Initialize clients
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
ytmusic = YTMusic()

def download_ffmpeg():
    print("Downloading FFmpeg...")
    if sys.platform.startswith('win'):
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = "ffmpeg.zip"
        ffmpeg_path = "ffmpeg.exe"
    else:
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        zip_path = "ffmpeg.tar.xz"
        ffmpeg_path = "ffmpeg"

    response = requests.get(url)
    with open(zip_path, 'wb') as f:
        f.write(response.content)

    if sys.platform.startswith('win'):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract(f"ffmpeg-master-latest-win64-gpl/bin/{ffmpeg_path}", ".")
        os.rename(f"ffmpeg-master-latest-win64-gpl/bin/{ffmpeg_path}", ffmpeg_path)
        shutil.rmtree("ffmpeg-master-latest-win64-gpl")
    else:
        subprocess.run(['tar', '-xf', zip_path])
        os.rename(f"ffmpeg-*-static/{ffmpeg_path}", ffmpeg_path)
        shutil.rmtree([d for d in os.listdir() if d.startswith("ffmpeg-") and os.path.isdir(d)][0])

    os.remove(zip_path)
    os.chmod(ffmpeg_path, 0o755)
    print(f"FFmpeg downloaded successfully to: {os.path.abspath(ffmpeg_path)}")
    return os.path.abspath(ffmpeg_path)

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if sys.platform.startswith('win'):
            bundled_ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
            if os.path.exists(bundled_ffmpeg):
                return bundled_ffmpeg
            # Check in the same directory as the executable
            exe_dir = os.path.dirname(sys.executable)
            ffmpeg_path = os.path.join(exe_dir, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        else:
            bundled_ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg')
            if os.path.exists(bundled_ffmpeg):
                return bundled_ffmpeg
            # Check in the same directory as the executable
            exe_dir = os.path.dirname(sys.executable)
            ffmpeg_path = os.path.join(exe_dir, 'ffmpeg')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
    else:
        # Running as script
        ffmpeg_path = which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
    
    # If not found, check in current working directory
    if sys.platform.startswith('win'):
        local_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg.exe')
    else:
        local_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg')
    
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    
    # If still not found, download it
    return download_ffmpeg()

def check_ffmpeg():
    ffmpeg_path = get_ffmpeg_path()
    try:
        result = subprocess.run([ffmpeg_path, '-version'], check=True, capture_output=True, text=True)
        print(f"FFmpeg found at: {ffmpeg_path}")
        print(f"FFmpeg version: {result.stdout.split('version')[1].split()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error checking FFmpeg at {ffmpeg_path}: {str(e)}")
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
    except Exception as e:
        print(f"Error getting track info: {str(e)}")
        return None

def get_playlist_tracks(playlist_url):
    try:
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        results = sp.playlist_tracks(playlist_id)
        return [{
            'name': item['track']['name'],
            'artist': item['track']['artists'][0]['name'],
            'album': item['track']['album']['name']
        } for item in results['items']]
    except Exception as e:
        print(f"Error getting playlist tracks: {str(e)}")
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

        ffmpeg_path = get_ffmpeg_path()
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
            'ffmpeg_location': ffmpeg_path,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return os.path.exists(f"{output_template}.mp3")
    except Exception as e:
        print(f"Error downloading track: {str(e)}")
        return False

def process_url(url):
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

def main():
    if not check_ffmpeg():
        print("FFmpeg is not installed. Attempting to download...")
        ffmpeg_path = download_ffmpeg()
        if not check_ffmpeg():
            print("Failed to download and install FFmpeg. Please install it manually.")
            return

    url = input("Enter the Spotify track or playlist URL: ")
    process_url(url)

if __name__ == "__main__":
    main()
