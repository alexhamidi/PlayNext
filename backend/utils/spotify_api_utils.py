from dotenv import load_dotenv
import os

load_dotenv()


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.spotify.com/v1/audio-analysis/"


async def fetch_single_song_data(session, song_id):
    url = f"{BASE_URL}{song_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            song_data = await response.json()
            track_data = song_data.get('track', {})
            keys_to_keep = ['duration', 'loudness', 'tempo', 'time_signature', 'key', 'mode'] # needs to be a 2d list
            song_data_filtered = [float(track_data[k]) for k in keys_to_keep]
            return song_data_filtered
        else:
            print(f"Request failed for {song_id} with status code: {response.status}")
            return None
