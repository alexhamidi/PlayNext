from typing import Optional
import io
import torch
from ml import SongClassifier
from redis_om import Field, HashModel, Migrator, NotFoundError
import warnings
warnings.filterwarnings("ignore", message="Field .* has conflict with protected namespace .*")


class Model(HashModel):
    model_name: str = Field(index=True, alias="name")
    nn_model_serialized: Optional[bytes] = Field(default=None)

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
    model = get_model(model_name)

    buffer = io.BytesIO()
    torch.save(nn_model.state_dict(), buffer)
    nn_model_serialized = buffer.getvalue()
    model.nn_model_serialized = nn_model_serialized

    model.save()

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
