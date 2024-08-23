import asyncio
import aiohttp
import torch
from utils.spotify_api_utils import fetch_single_song_data



async def song_ids_to_tensors(song_ids_flagged):
    features_list = []
    classes_list = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_song_data(session, song_id_flagged) for song_id_flagged in song_ids_flagged]
        results = await asyncio.gather(*tasks)
    # completely off
    print('succesfully fetched song data')
    for result in results:
        print(result)
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
