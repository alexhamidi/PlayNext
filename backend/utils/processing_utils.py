import asyncio
import aiohttp
import torch
import re
from utils.spotify_api_utils import *

def test_song_id_to_tensor(song_id):
    result = fetch_single_song_test_data(song_id)
    if result is None:
        print("data not processed properly")
    feature_tensor = torch.tensor(result, dtype=torch.float32)
    return feature_tensor

async def train_song_ids_to_tensors(song_ids_flagged): # generalize t
    features_list = []
    classes_list = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_song_train_data(session, song_id_flagged) for song_id_flagged in song_ids_flagged]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    print('Successfully fetched song data')
    for result in results:
        if isinstance(result, PermissionError):
            raise RuntimeError("Permission error occurred. Invalid API Key") from result
        elif isinstance(result, Exception):
            print(f"Error processing song: {result}")
        elif result is not None:
            song_features, song_class = result
            features_list.append(song_features)
            classes_list.append(song_class)

    if not features_list:
        raise ValueError("No valid song data was processed")

    features_tensor = torch.tensor(features_list, dtype=torch.float32)
    classes_tensor = torch.tensor(classes_list)

    return features_tensor, classes_tensor

def raw_input_to_song_ids(data):
    pattern = r"^https://open\.spotify\.com/track/([a-zA-Z0-9]{22})$"
    ids = []
    for url in data.splitlines():
        match = re.match(pattern, url)
        if not match:
            raise ValueError(f"Incorrect data format: {url}")
        ids.append(match.group(1))
    return ids
