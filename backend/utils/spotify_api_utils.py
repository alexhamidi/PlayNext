from dotenv import load_dotenv
import os
import requests

load_dotenv()


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.spotify.com/v1/audio-analysis/"
KEYS_TO_USE = []

def fetch_single_song_test_data(song_id):
    url = f"{BASE_URL}{song_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try: # synchronous request for one item
        response = requests.get(url, headers=headers)
        if response.status == 200:
            song_data = response.json()
            song_data_filtered = filter_spotify_response(song_data)
            return song_data_filtered
        elif response.status == 401:
            raise PermissionError(f"Incorrent API Key/invalid authorization")
        elif response.status == 404:
            raise FileNotFoundError(f"URL not found:{url}")
        else:
            print(f"Request failed for {song_id} with status code: {response.status}")
            return None
    except requests.RequestException as e:
        print(f"Request failed for {song_id}: {str(e)}")
        return None

async def fetch_single_song_train_data(session, song_id_flagged):
    song_id = song_id_flagged[0]
    song_class = song_id_flagged[1]
    url = f"{BASE_URL}{song_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    async with session.get(url, headers=headers) as response: # asynchronous request for one item
        if response.status == 200:
            song_data = await response.json()
            song_data_filtered = filter_spotify_response(song_data)
            return song_data_filtered, song_class
        elif response.status == 401:
            raise PermissionError(f"Incorrent API Key/invalid authorization")
        elif response.status == 404:
            raise FileNotFoundError(f"URL not found:{url}")
        else:
            print(f"Request failed for {song_id} with status code: {response.status}")
            return None

def filter_spotify_response(song_data):
    track_data = song_data.get('track', {})
    song_data_filtered = [float(track_data[k]) for k in KEYS_TO_USE]
    return song_data_filtered
