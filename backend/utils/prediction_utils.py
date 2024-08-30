
from global_constants import NUM_RETRIES_PER_BATCH, REC_BATCH_SIZE, POSITIVE_THRESHOLD
from utils.song_db_utils import get_random_song_ids
from utils.processing_utils import song_ids_to_feature_tensors
from ml import get_positive_examples

async def get_song_predictions(nn_model, num_recommendations): # maybe move this somewhere else
    predicted_ids = []
    minimum_batches = -(-num_recommendations // REC_BATCH_SIZE)
    total_retries_left = NUM_RETRIES_PER_BATCH * minimum_batches

    while len(predicted_ids) < num_recommendations and total_retries_left > 0:
        total_retries_left -= 1

        current_song_ids = await get_random_song_ids(REC_BATCH_SIZE)
        current_songs_features_tensor, processed_song_ids_tensor = await song_ids_to_feature_tensors(current_song_ids, True)

        current_predicted_ids = get_positive_examples(nn_model, current_songs_features_tensor, processed_song_ids_tensor)

        remaining = num_recommendations - len(predicted_ids)
        predicted_ids.extend(current_predicted_ids[:remaining])

    if len(predicted_ids) < num_recommendations:
        print(f"Warning: Only generated {len(predicted_ids)} recommendations.")

    return predicted_ids
