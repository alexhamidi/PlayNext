from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ml import *
from utils.db_utils import *
from utils.processing_utils import *
from utils.spotify_api_utils import *
import uvicorn


# redis - use to store song information by id
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='http://localhost:8080',
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class ModelRequest(BaseModel):
    model_name:str

class TrainRequest(BaseModel):
    positive_examples:  list[str]
    negative_examples: list[str]
    model_name:str

# maybe dont even need to interface with the db here - only in utils

@app.get("/models")
def get_models():
    try:
        models = get_all_models_and_num_songs()
        return  {"message": "Models retreived succesfully", "models":models}
    except Exception as e: # be more descriptive - conflict
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models")
def init_model(request: ModelRequest):
    try:
        model_name = request.model_name
        add_model(model_name)
        return {"message": "Model Initialized successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_model(request: TrainRequest):
    try:
        print("Fetching request values...")
        model_name = request.model_name
        positive_data = request.positive_examples
        negative_data = request.negative_examples

        print("Converting input into song ids...")
        positive_example_ids = raw_input_to_song_ids(positive_data)
        negative_example_ids = raw_input_to_song_ids(negative_data)

        print("Combining and flagging ids...")
        example_ids_flagged = [(positive_example, 1) for positive_example in positive_example_ids] + [(negative_example, 0) for negative_example in negative_example_ids]

        print("Converting ids to feature tensors...")
        features_tensor, classes_tensor = await train_song_ids_to_tensors(example_ids_flagged)

        print("Getting the model associated with the user ...")
        nn_model = get_nn_model(model_name)

        print("Model succesfully gotten")

        if (nn_model is None):
            nn_model = init_nn_model()
            nn_model, num_new_songs = train_nn_model(nn_model, features_tensor, classes_tensor, 100, .001)
        else:
            nn_model, num_new_songs = train_nn_model(nn_model, features_tensor, classes_tensor, 100, .001)

        update_num_songs(model_name, num_new_songs)
        add_nn_model(model_name, nn_model)

        return  {"message": "Model trained successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendation")
async def get_recommendation(request: ModelRequest):
    try:
        model_name = request.model_name
        print('model_name: ', model_name)

        # this is not being executed properly
        nn_model = get_nn_model(model_name)

        # error here
        predicted_id = get_single_song_prediction(nn_model)

        print('predicted id: ', predicted_id)
        # something is happening here
        if predicted_id is None:
            raise Exception(f"no matches found for the model {model_name} after {NUM_RETRIES} attempts")
        else:
            predicted_uri = convert_song_id_to_uri(predicted_id)
            print('predicted_uri:', predicted_uri)
        return {"message": "Prediction retreived successfully", "predicted_uri":predicted_uri}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8040, reload=True)


