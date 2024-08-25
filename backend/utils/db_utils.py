import torch
import io
from ml import SongClassifier
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
    # big todo - num_songs_trained
    class Meta:
        database = mdb_rom # any operations will default to this dataabse
        global_key_prefix = ""
Migrator().run()

def add_model(model_name):
    model = Model(model_name=model_name)
    model.save()

def get_model(model_name):
    try:
        return Model.find(Model.model_name == model_name).first()
    except NotFoundError:
        return None

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
    nn_model_base64 = model.nn_model_serialized
    if nn_model_base64 == '':
        print("nn_model is none")
        return None
    try:
        print("model is not none")
        # Decode the base64 encoded serialized model
        nn_model_serialized = base64.b64decode(nn_model_base64.encode('ascii'))
        buffer = io.BytesIO(nn_model_serialized)
        state_dict = torch.load(buffer)
        nn_model = SongClassifier()
        nn_model.load_state_dict(state_dict)
        return nn_model
    except Exception as e:
        print(f"Error deserializing model: {e}")
        return None

def get_all_model_names():
    pattern = ':utils.db_utils.Model:*'
    cursor = -1
    model_names = []

    while cursor != 0:
        cursor += cursor == -1
        cursor, keys = mdb_r.scan(cursor=cursor, match=pattern)
        for key in keys:
            if mdb_r.type(key) == 'hash':
                model_data = mdb_r.hgetall(key)
                model_name = model_data.get('model_name', None)
                if model_name:
                    model_names.append(model_name)

    return model_names

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
    song_count = int(sdb.get(COUNT_KEY))
    random_index = random.randint(0, song_count - 1)
    result_as_bytes = sdb.hget(HASH_KEY, random_index)
    return result_as_bytes.decode('utf-8')

def list_all_db_items(db):
    r = redis.Redis(host='localhost', port=6379, db=db)
    keys = r.keys()
    for key in keys:
        key_type = r.type(key).decode('utf-8')
        print(f"Key: {key.decode('utf-8')}, Type: {key_type}")
        if key_type == 'hash':
            data = r.hgetall(key)
            for field, value in data.items():
                print(f"  {field.decode('utf-8')}: {value.decode('utf-8')}")
        elif key_type == 'string':
            value = r.get(key)
            print(f"  Value: {value.decode('utf-8')}")


