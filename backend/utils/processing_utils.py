import asyncio
import aiohttp
import torch
from utils.spotify_api_utils import fetch_single_song_data

def get_class_tensor(goodids, badids, good_failed_ids, bad_failed_ids):
    classes = []
    for song_id in goodids:
        if song_id not in good_failed_ids:
            classes.append(1)
    for song_id in badids:
        if song_id not in bad_failed_ids:
            classes.append(1)
    return torch.tensor(classes)


async def song_ids_to_tensors(song_ids):
    features_list = []
    classes_list = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_song_data(session, song_id) for song_id in song_ids]
        results = await asyncio.gather(*tasks)

    for result in results:
        if result is not None:
            song_features, song_class = result
            features_list.append(song_features)
            classes_list.append(song_class)

    features_tensor = torch.tensor(features_list, dtype=torch.float32)
    classes_tensor = torch.tensor(classes_list)

    return features_tensor, classes_tensor

def raw_input_to_song_ids(data):
    ids = [url.split("/")[-1] for url in data.splitlines()]
    return ids

def ids_to_uris(ids):
    return [f'https://open.spotify.com/track/{id}' for id in ids]
