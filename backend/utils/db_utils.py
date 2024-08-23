from typing import Optional
import io
import torch
from ml import SongClassifier
from redis_om import Field, HashModel, Migrator, NotFoundError
import warnings
warnings.filterwarnings("ignore", message="Field .* has conflict with protected namespace .*")
import base64


from redis_om import get_redis_connection

redis = get_redis_connection(
    host="localhost",
    port=6379,
    decode_responses=False
)

class Model(HashModel):
    model_name: str = Field(index=True)
    nn_model_serialized: bytes = Field(default=b'')
    class Meta:
        database = redis
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

    model.nn_model_serialized = bytes(nn_model_serialized)
    print("Serialized model assigned to model object")

    try:
        model.save()
        print("Model saved successfully")
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        print(f"Model object: {model}")
        print(f"Model name: {model.model_name}")
        print(f"Serialized data size: {len(model.nn_model_serialized)} bytes")
        print(f"First 20 bytes of serialized data: {model.nn_model_serialized[:20]}")

    return model

def get_nn_model(model_name):
    model = get_model(model_name)
    nn_model_serialized = model.nn_model_serialized
    if nn_model_serialized is None:
        return None
    try:
        buffer = io.BytesIO(model.nn_model_serialized)
        state_dict = torch.load(buffer)
        nn_model = SongClassifier()
        nn_model.load_state_dict(state_dict)
        return nn_model
    except Exception as e:
        print(f"Error deserializing model: {e}")
        return None

