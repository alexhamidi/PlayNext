import asyncio
import aiohttp
import torch
import re
from utils.spotify_api_utils import *

TRACK_URL = 'https://open.spotify.com/track'
TRACK_PATTERN = r"^https://open\.spotify\.com/track/([a-zA-Z0-9]{22})$"

def test_song_id_to_tensor(song_id):
    print('fetching single song data:')
    result = fetch_single_song_test_data(song_id) # problem here
    print('song data: ', result)
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

def raw_input_to_song_ids(uris):
    ids = []
    for uri in uris:
        match = re.match(TRACK_PATTERN, uri)
        if not match:
            raise ValueError(f"Incorrect data format: {uri}")
        ids.append(match.group(1))
    return ids


def convert_song_id_to_uri(song_id):
    return TRACK_URL + '/' + song_id

def convert_song_ids_to_uris(song_ids):
    return [convert_song_id_to_uri(song_id) for song_id in song_ids]
