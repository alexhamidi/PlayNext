#=======================================================================#
# IMPORTS
#=======================================================================#
import asyncio
import aiohttp
import torch
import re
from utils.spotify_api_utils import *
from global_constants import TRACK_URL, TRACK_PATTERN

#=======================================================================#
# async def song_ids_to_feature_tensors(song_ids, is_test, classes=None):
# always returns 2 tensors. The first will always be the feature tensors
# associated with the ids. If it is in test mode, it will return the song
# ids as well, if it is in train mode, it will return classes (labels).
#=======================================================================#
async def song_ids_to_feature_tensors(song_ids, is_test, token, classes=None):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_song_data(session, song_id, token) for song_id in song_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    print('Successfully fetched song data')

    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, PermissionError):
            raise RuntimeError("Permission error occurred. Invalid API Key") from result
        elif result is not None:
            valid_results.append((i, result))

    if not valid_results:
        raise ValueError("No valid song data was processed")

    features_list = [result for _, result in valid_results] # all song ids
    features_tensor = torch.tensor(features_list, dtype=torch.float32) # convert

    if is_test:
        classes_list = [classes[i] for i, _ in valid_results]
        classes_tensor = torch.tensor(classes_list)
        return features_tensor, classes_tensor
    else:
        processed_song_ids = [song_ids[i] for i, _ in valid_results]
        song_ids_tensor = torch.tensor(processed_song_ids)
        return features_tensor, song_ids_tensor

#=======================================================================#
# def raw_input_to_song_ids(uris): converts a list of uris to a list of
# ids
#=======================================================================#
def raw_input_to_song_ids(uris):
    ids = []
    for uri in uris:
        match = re.match(TRACK_PATTERN, uri)
        if not match:
            raise ValueError(f"Incorrect data format: {uri}")
        ids.append(match.group(1))
    return ids

#=======================================================================#
# Returns a list of song ids converted to track uris
#=======================================================================#
def convert_song_ids_to_uris(song_ids):
    return [TRACK_URL + '/' + song_id for song_id in song_ids]
