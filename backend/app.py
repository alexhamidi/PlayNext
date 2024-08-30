
#=======================================================================#
# IMPORTS
#=======================================================================#
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ml import *
from utils.model_db_utils import get_all_models_and_num_songs, add_model, get_nn_model, add_nn_model, update_num_songs
from utils.processing_utils import raw_input_to_song_ids, song_ids_to_feature_tensors, convert_song_ids_to_uris
from utils.prediction_utils import get_song_predictions
from utils.app_utils import api_handler
import uvicorn

#=======================================================================#
# CONFIGURE THE APP AND CORS
#=======================================================================#
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='http://localhost:8080',
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

#=======================================================================#
# DECLARE REQUEST TYPES
#=======================================================================#
class ModelRequest(BaseModel):
    model_name:str

class BulkRequest(BaseModel):
    model_name:str
    num_recommendations:int

class TrainRequest(BaseModel):
    positive_examples:  list[str]
    negative_examples: list[str]
    model_name:str

#=======================================================================#
# GET /models: returns the model_names and num_songs of all db models.
#=======================================================================#
@app.get("/models")
@api_handler("GET", "models")
async def get_models():

    print('Retrieving all models...')
    models = get_all_models_and_num_songs()
    print('Models:', models)

    return  {"message": "Models retreived succesfully", "models":models}

#=======================================================================#
# POST /models: takes a new model name and adds it to the database
#=======================================================================#
@app.post("/models")
@api_handler("POST", "models")
def init_model(request: ModelRequest):
    model_name = request.model_name

    print(f"Adding model {model_name}...")
    add_model(model_name)

    return {"message": "Model Initialized successfully"}

#=======================================================================#
# POST /train: takes a model name and positive and negative training
# examples associated with it and trains the model
#=======================================================================#
@app.post("/train")
@api_handler("POST", "train")
async def train_model(request: TrainRequest):
    model_name = request.model_name
    positive_data = request.positive_examples
    negative_data = request.negative_examples

    print("Converting input into song ids...")
    positive_example_ids = raw_input_to_song_ids(positive_data)
    negative_example_ids = raw_input_to_song_ids(negative_data)

    print('Converting data into lists...')
    train_ids = positive_example_ids + negative_example_ids
    train_classes = [1] * len(positive_example_ids) + [0] * len(negative_example_ids)

    print("Converting ids to feature tensors...")
    features_tensor, classes_tensor = await song_ids_to_feature_tensors(train_ids, False, classes=train_classes)

    print("Getting the model associated with the user ...")
    nn_model = get_nn_model(model_name) or init_nn_model()

    print('Training nn model...')
    nn_model, num_new_songs = train_nn_model(nn_model, features_tensor, classes_tensor, 100, .001)

    print('Updating the number of songs the model has been trained on in the DB...')
    update_num_songs(model_name, num_new_songs)

    print('Adding the updated nn_model to the DB...')
    add_nn_model(model_name, nn_model)

    return {"message": "Model trained successfully"}

#=======================================================================#
# POST /recommendations: Returns a given number of positive examples.
#=======================================================================#
@app.post("/recommendations")
@api_handler("POST", "recommendations")
async def get_recommendations(request: BulkRequest):
    model_name = request.model_name
    num_recommendations = request.num_recommendations

    print("Getting the model associated with the user ...")
    nn_model = get_nn_model(model_name)

    print(f"Getting the {num_recommendations} predicted ids")
    predicted_ids = await get_song_predictions(nn_model, num_recommendations)

    print("Parsing the ids into utis")
    predicted_uris = convert_song_ids_to_uris(predicted_ids)

    return {"message": "Prediction retreived successfully", "predicted_uris":predicted_uris}


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8040, reload=True)


