from dotenv import load_dotenv
import os

load_dotenv()


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.spotify.com/v1/audio-analysis/"


async def fetch_single_song_data(session, song_id_flagged):
    song_id = song_id_flagged[0]
    song_class = song_id_flagged[1]
    url = f"{BASE_URL}{song_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            song_data = await response.json()
            track_data = song_data.get('track', {})
            keys_to_keep = ['duration', 'loudness', 'tempo', 'time_signature', 'key', 'mode'] # needs to be a 2d list
            song_data_filtered = [float(track_data[k]) for k in keys_to_keep]
            return song_data_filtered, song_class
        elif response.status == 401:
            raise PermissionError(f"Incorrent API Key/invalid authorization")
        elif response.status == 404:
            raise FileNotFoundError(f"URL not found:{url}")
        else:
            print(f"Request failed for {song_id} with status code: {response.status}")
            return None
