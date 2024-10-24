import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API credentials
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Rest of the code remains the same
