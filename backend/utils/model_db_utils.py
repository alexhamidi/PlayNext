#problem: oms and normals being save differently

#=======================================================================#
# IMPORTS
#=======================================================================#
import torch
import io
from nn_model import SongClassifier
from config import NUM_FEATURES, NUM_CLASSES
from redis_om import Field, HashModel, Migrator, NotFoundError, get_redis_connection
import warnings
warnings.filterwarnings("ignore", message="Field .* has conflict with protected namespace .*")
import base64
import redis

#=======================================================================#
# CONFIGURING MODEL CLASS AND CONNECTION
#=======================================================================# colors gray
model_redis_connection = get_redis_connection(
    host="localhost",
    port=6379,
    decode_responses=True, # Set to True to automatically decode responses
    db=0
)

class Model(HashModel):
    model_name: str = Field(index=True)
    nn_model_serialized: str = Field(default='')  # Store as base64 encoded string
    num_songs: int = Field(default = 0)
    class Meta:
        database = model_redis_connection # any operations will default to this dataabse
Migrator().run()

#=======================================================================#
# def add_model(model_name): Adds a new model with the given name to the
# database
#=======================================================================#
def add_model(model_name):
    existing_model = get_model(model_name)
    if (existing_model is not None):
        raise NameError('Error: model already exists with this name')
    model = Model(model_name=model_name)
    model.save()

#=======================================================================#
# def delete_model(model_name): Adds a new model with the given name to the
# database
#=======================================================================#
def delete_model(model_name):
    model = get_model(model_name)
    model.delete(model.pk)

#=======================================================================#
# def get_model(model_name): Returns the entire Model object associated
# with the given model name
#=======================================================================#
def get_model(model_name):
    try:
        # models = Model.find(Model.model_name != "WHAT").all()
        # print(models)
        # return
        model = Model.find(Model.model_name == model_name).first()
        return model

    except NotFoundError:
        return None

#=======================================================================#
# def update_num_songs(model_name, num_new_songs): increments the number
# songs in a given model's object by a given amount
#=======================================================================#
def update_num_songs(model_name, num_new_songs):
    model = get_model(model_name)
    model.num_songs += num_new_songs
    model.save()

#=======================================================================#
# def add_nn_model(model_name, nn_model): Adds an nn_model with the
# given name to the db
#=======================================================================#
def add_nn_model(model_name, nn_model):
    print(f"Function called: add_nn_model. Model name: {model_name}")

    model = get_model(model_name)
    print(f"Model retrieved: {model}")

    buffer = io.BytesIO()
    torch.save(nn_model.state_dict(), buffer)
    print("Model state dict saved to buffer")

    nn_model_serialized = buffer.getvalue()
    print(f"Serialized model size: {len(nn_model_serialized)} bytes")
    print(f"First 20 bytes of serialized model: {nn_model_serialized[:20]}")

    nn_model_base64 = base64.b64encode(nn_model_serialized).decode('ascii')
    model.nn_model_serialized = nn_model_base64
    print("Base64 encoded serialized model assigned to model object")

    model.save()
    return model

#=======================================================================#
# def get_nn_model(model_name): returns the nn_model object associated
# with a model name
#=======================================================================#
def get_nn_model(model_name):

    print(f"Retreiving the model object for {model_name}...")
    model = get_model(model_name) # issue with get_model
    print('Model retrieved: ', model) # model is none


    nn_model_base64 = model.nn_model_serialized
    if nn_model_base64 == '':
        print("nn_model is none")
        return None
    try:
        print("model is not none")

        nn_model_serialized = base64.b64decode(nn_model_base64.encode('ascii'))
        buffer = io.BytesIO(nn_model_serialized)
        state_dict = torch.load(buffer, weights_only=True)
        nn_model = SongClassifier(n_features=NUM_FEATURES, n_classes=NUM_CLASSES)
        nn_model.load_state_dict(state_dict)
        return nn_model
    except Exception as e:
        print(f"Error deserializing model: {e}")
        return None

#=======================================================================#
# def get_all_models_and_num_songs(): gets all the models in the database
# and the number of songs associated with them.
#=======================================================================#
def get_all_models_and_num_songs(): # not working properly
    r = redis.Redis(host='localhost', port=6379,db=0, decode_responses=True)
    pattern = '*Model*'
    cursor = 0
    models = []

    while True:
        cursor, keys = r.scan(cursor=cursor, match=pattern)
        for key in keys:
            if r.type(key) == 'hash':
                model_data = r.hgetall(key)
                model_name = model_data.get('model_name')
                model_num_songs = int(model_data.get('num_songs', -1))
                if model_name is not None and model_num_songs != -1:
                    models.append({
                        "name": model_name,
                        "numSongs": model_num_songs
                    })
        if cursor == 0:
            break

    return models
