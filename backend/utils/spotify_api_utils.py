from global_constants import AUDIO_URL, KEYS_TO_USE
from app import token_manager

async def fetch_single_song_data(session, song_id,):
    token = token_manager.get_token()
    url = f"{AUDIO_URL}{song_id}"
    headers = {"Authorization": f"Bearer {token}"}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            song_data = await response.json()
            song_data_filtered = filter_spotify_response(song_data)
            return song_data_filtered
        elif response.status == 401:
            raise PermissionError("Incorrect API Key/invalid authorization")
        else:
            print(f"Request failed for {song_id} with status code: {response.status}")
            return None

def filter_spotify_response(song_data):
    track_data = song_data.get('track', {})
    song_data_filtered = [float(track_data[k]) for k in KEYS_TO_USE]
    return song_data_filtered
