#=======================================================================#
# IMPORTS
#=======================================================================#
import asyncio
import aiohttp
import torch
import re
from utils.spotify_api_utils import *
from config import TRACK_URL, TRACK_PATTERN, MAX_FEATURE_EXAMPLES

#=======================================================================#
# async def song_ids_to_feature_tensors(song_ids, is_test, classes=None):
# always returns 2 tensors. The first will always be the feature tensors
# associated with the ids. The second is the ids that failed.
#=======================================================================#
async def song_ids_to_feature_tensor(song_ids):
    async with aiohttp.ClientSession() as session:
        audio_analyses = await asyncio.gather(*[fetch_audio_analysis(session, song_id) for song_id in song_ids]) # this returns all of the response.jsons, NOT the processed data
        feature_list = [process_audio_analysis(analysis) for analysis in audio_analyses if analysis is not None]  # this is a list of 3d np arrays

        if len(feature_list) == 0:
            raise ValueError("Error: No valid song data processed")

        feature_nparr = np.array(feature_list)

        print(feature_nparr.shape)
        print(failed_song_ids)

        return torch.tensor(feature_nparr, dtype=torch.float32), failed_song_ids


#=======================================================================#
# def process_audio_analysis(audio_analysis): converts all the 2d feature
# vectors into a 1d array with all of them
#=======================================================================#
def process_audio_analysis(audio_analysis):
    bars_features_2d = process_time_features(audio_analysis['bars']) # each of these is the features for the given parameters. it is a 3d array, and needs to be converted to a single row.Why are these tuples
    beats_features_2d =  process_time_features(audio_analysis['beats'])
    tatums_features_2d = process_time_features(audio_analysis['tatums'])
    segments_features_2d = process_segments(audio_analysis['segments'])

    print("bars shape: ", bars_features_2d.shape)
    print("beats shape: ", beats_features_2d.shape)
    print("tatums shape: ", tatums_features_2d.shape)
    print("segments shape: ", segments_features_2d.shape)

    all_features_3d = np.concatenate (
        (
            bars_features_2d,
            beats_features_2d,
            tatums_features_2d,
            segments_features_2d,
        ),
        axis = 1
    )

    total_feature_count = all_features_3d.shape[1]

    all_features_3d = np.reshape(all_features_3d, (MAX_FEATURE_EXAMPLES * total_feature_count))

    return all_features_3d

#=======================================================================#
# def process_time_features(data): Given all of the low level data for
# the bars/beats/tatums, this function extracts the info related to time
# and stores it in an example x 3 array (each item has 3 properties:
# start, duration, confidence)
#=======================================================================#
def process_time_features(data):
    features = np.zeros((MAX_FEATURE_EXAMPLES, 3)) #2d array: num features, num data per feature
    for i, item in enumerate(data[:MAX_FEATURE_EXAMPLES]): # when going through, i is the index of the siong, and the number is which feature.
        features[i, 0] = item['start'] #
        features[i, 1] = item['duration']
        features[i, 2] = item['confidence']
    return features

#=======================================================================#
# def process_segments(data): Given all of the low level data for
# the song, this function extracts the info related to segments and stores it
# in an example x 3 array (each item has 31 properties)
#=======================================================================#
def process_segments(data): # number of songs being processed
    features = np.zeros((MAX_FEATURE_EXAMPLES, 31))  #  31 = 3 + 1 + 3 + 12 + 12
    for i, segment in enumerate(data[:MAX_FEATURE_EXAMPLES]):
        features[i, 0] = segment['start']
        features[i, 1] = segment['duration']
        features[i, 2] = segment['confidence']
        features[i, 3] = segment['loudness_start']
        features[i, 4] = segment['loudness_max']
        features[i, 5] = segment['loudness_max_time']
        features[i, 6] = segment['loudness_end']
        features[i, 7:19] = segment['pitches']
        features[i, 19:] = segment['timbre'] # 12 timberes
    return features

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
