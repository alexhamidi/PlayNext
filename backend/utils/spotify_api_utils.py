from global_constants import API_KEY, AUDIO_URL, KEYS_TO_USE

async def fetch_single_song_data(session, song_id):
    url = f"{AUDIO_URL}{song_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
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
