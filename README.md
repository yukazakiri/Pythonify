# Pythonify

![Build Status](https://github.com/yukazakiri/pythonify/workflows/Build%20Pythonify/badge.svg)

## Overview

Pythonify is a powerful, cross-platform tool that allows you to download your favorite tracks and playlists from Spotify as high-quality MP3 files. It uses the Spotify API to fetch track information and YouTube Music to source the audio, ensuring the best possible match and audio quality.

## Features

- Download individual Spotify tracks
- Download entire Spotify playlists
- High-quality MP3 conversion (192kbps)
- Cross-platform support (Windows, macOS, Linux)
- Elegant command-line interface with progress bars
- Automatic retries on failed downloads

## Prerequisites

- Python 3.9 or higher
- FFmpeg installed and accessible from the system PATH

## Installation

1. Clone this repository:   ```
   git clone https://github.com/yukazakiri/pythonify.git
   cd pythonify   ```

2. Install the required dependencies:   ```
   pip install -r requirements.txt   ```

3. Set up your Spotify API credentials:
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Create a new application
   - Copy the Client ID and Client Secret
   - Replace the placeholders in `pythonify.py` with your credentials:     ```python
     CLIENT_ID = 'Your Spotify Client ID'
     CLIENT_SECRET = 'Your Spotify Client Secret'     ```

## Usage

Run the script using Python:

## Configuration

Create a `.env` file in the same directory as the executable with the following content:

```
SPOTIFY_CLIENT_ID={Your Spotify Client ID}
SPOTIFY_CLIENT_SECRET={Your Spotify Client Secret}
```
