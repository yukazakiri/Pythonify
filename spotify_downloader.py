import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from ytmusicapi import YTMusic
import os
import time
import random
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Rich console
console = Console()

# Spotify API credentials
client_id = '471d9253fa4b4deb82ffaddc8c7d3510'
client_secret = 'bb608567541a4adf857d0e87a2c1b5f1'

# Initialize Spotify client
try:
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    logging.info("Spotify API client initialized successfully")
except spotipy.SpotifyException as e:
    logging.error(f"Error initializing Spotify client: {e}")
    sys.exit(1)

# Initialize YouTube Music client
ytmusic = YTMusic()

def get_track_info(track_url):
    try:
        track_id = track_url.split('/')[-1].split('?')[0]
        track_info = sp.track(track_id)
        logging.info(f"Successfully fetched track info for {track_id}")
        return {
            'name': track_info['name'],
            'artist': track_info['artists'][0]['name'],
            'album': track_info['album']['name']
        }
    except spotipy.SpotifyException as e:
        logging.error(f"Error fetching track info: {e}")
        return None

def download_track(track_info):
    if not track_info:
        console.print("[bold red]No track information available. Aborting download.[/bold red]")
        return

    query = f"{track_info['name']} {track_info['artist']}"
    output_template = f"{track_info['name']} - {track_info['artist']}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                
                search_task = progress.add_task("Searching YouTube Music...", total=None)
                search_results = ytmusic.search(query, filter="songs", limit=1)
                if not search_results:
                    raise Exception("No track found on YouTube Music")
                progress.update(search_task, completed=True, description="YouTube Music search successful")
                
                video_id = search_results[0]['videoId']
                video_url = f"https://music.youtube.com/watch?v={video_id}"
                logging.info(f"Video URL: {video_url}")
                
                download_task = progress.add_task("Downloading and Converting...", total=100)
                
                def yt_dlp_hook(d):
                    if d['status'] == 'downloading':
                        progress.update(download_task, completed=float(d['downloaded_bytes'])/float(d['total_bytes'])*100)
                    elif d['status'] == 'finished':
                        progress.update(download_task, completed=100)

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
                    'progress_hooks': [yt_dlp_hook],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                mp3_file = f"{output_template}.mp3"
                if not os.path.exists(mp3_file):
                    raise FileNotFoundError(f"MP3 file not found: {mp3_file}")

            console.print(Panel(f"[bold green]Successfully downloaded and converted:[/bold green]\n[cyan]{track_info['name']}[/cyan] by [cyan]{track_info['artist']}[/cyan]"))
            
            # Get the full path of the MP3 file
            full_path = os.path.abspath(mp3_file)
            console.print(f"[bold]File saved at:[/bold] {full_path}")
            
            return
        except FileNotFoundError as e:
            console.print(f"[bold red]File not found error:[/bold red] {str(e)}")
        except Exception as e:
            console.print(f"[bold red]Attempt {attempt + 1} failed:[/bold red] {str(e)}")
        
        if attempt < max_retries - 1:
            wait_time = random.uniform(5, 10)
            with console.status(f"[bold yellow]Retrying in {wait_time:.2f} seconds...[/bold yellow]"):
                time.sleep(wait_time)
        else:
            console.print(f"[bold red]Failed to download and convert after {max_retries} attempts.[/bold red]")

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        logging.info("FFmpeg is installed and accessible")
        return True
    except subprocess.CalledProcessError:
        console.print("[bold red]FFmpeg is not installed or not accessible[/bold red]")
        return False
    except FileNotFoundError:
        console.print("[bold red]FFmpeg is not installed or not in the system PATH[/bold red]")
        return False

def main():
    console.print(Panel.fit("[bold cyan]Spotify Track Downloader[/bold cyan]", border_style="bold"))
    
    if not check_ffmpeg():
        console.print("[bold red]Please install FFmpeg and make sure it's in your system PATH[/bold red]")
        return

    track_url = console.input("[bold green]Enter the Spotify track URL: [/bold green]")
    with console.status("[bold blue]Fetching track information...[/bold blue]"):
        track_info = get_track_info(track_url)
    
    if track_info:
        download_track(track_info)
    else:
        console.print("[bold red]Failed to get track information. Please check your Spotify URL and try again.[/bold red]")

if __name__ == "__main__":
    main()
