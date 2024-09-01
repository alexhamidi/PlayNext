
from config import NUM_RETRIES_PER_PREDICTION_BATCH, REC_BATCH_SIZE, POSITIVE_THRESHOLD
from utils.song_db_utils import get_random_song_ids
from utils.processing_utils import song_ids_to_feature_tensor
from ml import get_positive_examples

async def get_song_predictions(nn_model, num_recommendations): # maybe move this somewhere else
    predicted_ids = []
    minimum_batches = -(-num_recommendations // REC_BATCH_SIZE)
    total_retries_left = NUM_RETRIES_PER_PREDICTION_BATCH * minimum_batches

    while len(predicted_ids) < num_recommendations and total_retries_left > 0:
        total_retries_left -= 1

        current_song_ids = await get_random_song_ids(REC_BATCH_SIZE)
        current_songs_features_tensor, failed_song_ids = await song_ids_to_feature_tensor(current_song_ids)

        not_failed_song_ids = [song_id for song_id in current_song_ids if song_id not in failed_song_ids]

        print('Current songs feature tensor size:', current_songs_features_tensor.size(dim=0))
        print('Song ids list:', len(not_failed_song_ids))

        if current_songs_features_tensor.size(dim=0) != len(not_failed_song_ids):
            raise ValueError("Error: Not a 1 to one mapping between song ids and features")

        current_predicted_ids = get_positive_examples(nn_model, current_songs_features_tensor, not_failed_song_ids) # i think the problem is here, since the previous are fine. always empty

        print('Current predicted ids:', current_predicted_ids) # never populating properly

        print('RETRIEVED POSITIVE_EXAMPLES:', len(current_predicted_ids))

        remaining = num_recommendations - len(predicted_ids)
        predicted_ids.extend(current_predicted_ids[:remaining])

    if len(predicted_ids) < num_recommendations:
        raise ValueError("ERROR: Unable to get all recommendations")

    return predicted_ids
