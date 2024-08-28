import torch
import io
from utils.nn_model import SongClassifier
from utils.spotify_api_utils import KEYS_TO_USE
from redis_om import Field, HashModel, Migrator, NotFoundError, get_redis_connection
import warnings
warnings.filterwarnings("ignore", message="Field .* has conflict with protected namespace .*")
import base64
import redis
'''''''''''''''''''''''''''''
MODEL_UTILS
'''''''''''''''''''''''''''''

mdb_rom = get_redis_connection(
    host="localhost",
    port=6379,
    decode_responses=True, # Set to True to automatically decode responses
    db=0
)

mdb_r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

class Model(HashModel):
    model_name: str = Field(index=True)
    nn_model_serialized: str = Field(default='')  # Store as base64 encoded string
    num_songs: int = Field(default = 0)
    class Meta:
        database = mdb_rom # any operations will default to this dataabse
        global_key_prefix = ""
Migrator().run()

def add_model(model_name):
    existing_model = get_model(model_name)
    if (existing_model is not None):
        raise Exception('Error: model already exists with this name')
    model = Model(model_name=model_name)
    model.save()

def get_model(model_name):
    try:
        return Model.find(Model.model_name == model_name).first()
    except NotFoundError:
        return None

def update_num_songs(model_name, num_new_songs):
    model = get_model(model_name)
    model.num_songs += num_new_songs
    model.save()

def add_nn_model(model_name, nn_model):
    print("Function called: add_nn_model")
    print(f"Model name: {model_name}")

    model = get_model(model_name)
    print(f"Model retrieved: {model}")

    buffer = io.BytesIO()
    torch.save(nn_model.state_dict(), buffer)
    print("Model state dict saved to buffer")

    nn_model_serialized = buffer.getvalue()
    print(f"Serialized model size: {len(nn_model_serialized)} bytes")
    print(f"First 20 bytes of serialized model: {nn_model_serialized[:20]}")

    # Encode the serialized model as base64
    nn_model_base64 = base64.b64encode(nn_model_serialized).decode('ascii')
    model.nn_model_serialized = nn_model_base64
    print("Base64 encoded serialized model assigned to model object")

    try:
        model.save()
        print("Model saved successfully")
        return model
    except Exception as e:
        raise Exception(f"Error saving model: {str(e)}")


def get_nn_model(model_name):
    model = get_model(model_name)
    num_songs = model.num_songs
    nn_model_base64 = model.nn_model_serialized
    if nn_model_base64 == '':
        print("nn_model is none")
        return None
    try:
        print("model is not none")
        num_features = len(KEYS_TO_USE)
        num_classes = 2
        # Decode the base64 encoded serialized model
        nn_model_serialized = base64.b64decode(nn_model_base64.encode('ascii'))
        buffer = io.BytesIO(nn_model_serialized)
        state_dict = torch.load(buffer, weights_only=True)
        nn_model = SongClassifier(n_features=num_features, n_classes=num_classes) # problem here
        nn_model.load_state_dict(state_dict)
        return nn_model
    except Exception as e:
        print(f"Error deserializing model: {e}")
        return None

def get_all_models_and_num_songs():
    pattern = ':utils.db_utils.Model:*'
    cursor = -1
    models = []  # Change this to a list instead of a dictionary

    while cursor != 0:
        cursor += cursor == -1
        cursor, keys = mdb_r.scan(cursor=cursor, match=pattern)
        for key in keys:
            if mdb_r.type(key) == 'hash':
                model_data = mdb_r.hgetall(key)
                model_name = model_data.get('model_name')
                model_num_songs = int(model_data.get('num_songs', -1))  # Assuming 'num_songs' is the correct key
                if model_name is not None and model_num_songs != -1:
                    models.append({
                        "name": model_name,
                        "numSongs": model_num_songs
                    })
    return models

'''''''''''''''''''''''''''''
SONG_UTILS
'''''''''''''''''''''''''''''
import redis
import random

sdb = redis.Redis(
    host='localhost',
    port=6379,
    db=1
)

HASH_KEY = "song_ids"
COUNT_KEY = "num_song_ids"

def get_random_song_id():
    print('called randomizer')
    song_count = int(sdb.get(COUNT_KEY)) # error in this linee
    print('end randomizer call')
    random_index = random.randint(0, song_count - 1)
    result_as_bytes = sdb.hget(HASH_KEY, random_index)
    return result_as_bytes.decode('utf-8')

