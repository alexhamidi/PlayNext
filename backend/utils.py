import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import numpy as np
import torch
from torch import nn

load_dotenv()

np.random.seed(42)
torch.manual_seed(42)

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.spotify.com/v1/audio-analysis/"

async def song_ids_to_feature_tensor(goodids, badids):
    all_ids = [(id, 1) for id in goodids] + [(id, 0) for id in badids]
    features = []
    #starts a session
    #ensures that the session is closed when we finish
    async with aiohttp.ClientSession() as session: # this syntax makes session an instance of a Clientsession.
        tasks = [fetch_single_song_data(session, song_id, song_class) for song_id, song_class in all_ids] # this is where the tuple s used
        #_build up all the tasks and the asycio gathers them and executes them properly
        results = await asyncio.gather(*tasks) #runs tasks concurrently #unpacks the tasks as separate
        features = [result for result in results if result is not None] # filter through to make sure that no examples are null

    return features

async def fetch_single_song_data(session, song_id, song_class):
    url = f"{BASE_URL}{song_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            song_data = await response.json()
            track_data = song_data.get('track', {})
            keys_to_keep = ['duration', 'loudness', 'tempo', 'time_signature', 'key', 'mode']
            song_data_filtered = {k: track_data[k] for k in keys_to_keep}
            song_data_filtered['class'] = song_class
            song_data_filtered['id'] = song_id
            return song_data_filtered
        else:
            print(f"Request failed for {song_id} with status code: {response.status}")
            return None

def raw_input_to_song_ids(gooddata, baddata):
    goodids = [url.split("/")[-1] for url in gooddata.splitlines()]
    badids = [url.split("/")[-1] for url in baddata.splitlines()]
    return goodids, badids