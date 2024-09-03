import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate and retrieve Spotify API credentials
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

if not client_id or not client_secret:
    logger.error("Spotify client credentials not found. Please check your .env file.")
    raise ValueError("Spotify client credentials not found. Please check your .env file.")

# Initialize Spotify client with authentication
try:
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    logger.info("Spotify client successfully authenticated.")
except Exception as e:
    logger.exception("Failed to authenticate with Spotify API.")
    raise ConnectionError(f"Failed to authenticate with Spotify API: {e}")

# Create the Flask app
app = Flask(__name__)

# It is recommended to use an environment variable for the secret key in a production environment
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Replace with a more secure key in production


def find_song(query):
    try:
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            song = results['tracks']['items'][0]
            return song['id'], song['name'], song['artists'][0]['name']
        else:
            return None, None, None
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Error during song search: {e}")
        return None, None, None
    except Exception as e:
        logger.exception("Unexpected error during song search.")
        return None, None, None


def get_recommendations(seed_song_id):
    try:
        recommendations = sp.recommendations(seed_tracks=[seed_song_id], limit=5)
        if not recommendations['tracks']:
            return []
        return [(track['name'], track['artists'][0]['name']) for track in recommendations['tracks']]
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Error during fetching recommendations: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error during fetching recommendations.")
        return []


def get_song_suggestions(query):
    try:
        results = sp.search(q=query, type='track', limit=5)
        if results['tracks']['items']:
            return [(track['id'], track['name'], track['artists'][0]['name']) for track in results['tracks']['items']]
        else:
            return []
    except Exception as e:
        logger.exception("Error during song suggestion search.")
        return []


# New route for handling AJAX requests for song suggestions
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    suggestions = get_song_suggestions(query)
    return jsonify(suggestions)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        song_name = request.form.get('song_name')
        if not song_name:
            flash("Please enter a song name with the artist.")
            return redirect(url_for('index'))

        song_id, song_title, artist = find_song(song_name)
        if song_id:
            recommendations = get_recommendations(song_id)
            return render_template('index.html', song_title=song_title, artist=artist, recommendations=recommendations)
        else:
            flash("Song not found. Please try a different search.")
            return redirect(url_for('index'))

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
