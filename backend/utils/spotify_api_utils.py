import asyncio
import aiohttp
import numpy as np
from config import AUDIO_ANALYSIS_URL, MAX_API_RETRIES_PER_SONG, RATE_LIMIT_DELAY
from tokenmanager import token_manager

failed_song_ids = []

async def fetch_audio_analysis(session, song_id):
    TOKEN = token_manager.get_token()
    url = f"{AUDIO_ANALYSIS_URL}{song_id}"
    headers = {"Authorization": f"Bearer {TOKEN}"}

    for _ in range(MAX_API_RETRIES_PER_SONG):
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    print(1)
                    return await response.json() # gets the bylk
                elif response.status == 401:
                    raise PermissionError("Incorrect API Key/invalid authorization")
                elif response.status == 429:
                    print(0)
                    retry_after = int(response.headers.get('Retry-After', RATE_LIMIT_DELAY))
                    await asyncio.sleep(retry_after)
                else:
                    print(f"Request failed for {song_id} with status code: {response.status}")
                    failed_song_ids.append(song_id)
                    return None
        except aiohttp.ClientError as e:
            print(f"ClientError occurred for {song_id}: {e}")
            await asyncio.sleep(1)

    print(f"Max retries reached for {song_id}")
    failed_song_ids.append(song_id)
    return None



