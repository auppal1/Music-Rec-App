import os
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Spotify API credentials
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

# Validate Spotify credentials
if not client_id or not client_secret:
    raise ValueError("Spotify client credentials not found. Please check your .env file.")

# Initialize Spotify client with authentication
try:
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
except Exception as e:
    raise ConnectionError(f"Failed to authenticate with Spotify API: {e}")


def find_song(query):
    """
    Search for a song on Spotify.

    Args:
        query (str): The search query including the song name and artist.

    Returns:
        str: The Spotify track ID of the found song, or None if no song is found.
    """
    try:
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            song = results['tracks']['items'][0]
            print(f"Found: {song['name']} by {song['artists'][0]['name']}")
            return song['id']
        else:
            print("Song not found.")
            return None
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error during song search: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during song search: {e}")
        return None


def get_recommendations(seed_song_id):
    """
    Get recommended songs based on a seed song.

    Args:
        seed_song_id (str): The Spotify track ID of the seed song.

    Returns:
        None
    """
    try:
        recommendations = sp.recommendations(seed_tracks=[seed_song_id], limit=5)
        if not recommendations['tracks']:
            print("No recommendations found.")
            return

        for idx, track in enumerate(recommendations['tracks']):
            print(f"{idx + 1}: {track['name']} by {track['artists'][0]['name']}")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error during fetching recommendations: {e}")
    except Exception as e:
        print(f"Unexpected error during fetching recommendations: {e}")


def main():
    """Main function to execute the script."""
    try:
        song_name = input("Please enter a song name with the artist: ")
        song_id = find_song(song_name)
        if song_id:
            print("\nRecommended Songs:")
            get_recommendations(song_id)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()