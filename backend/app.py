from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ml import *
from utils.db_utils import *
from utils.processing_utils import *
from utils.spotify_api_utils import *
import uvicorn

NUM_RETRIES = 500

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
    positive_examples: str
    negative_examples: str
    model_name:str

# maybe dont even need to interface with the db here - only in utils

@app.post("/model_exists")
def model_exists(request: ModelRequest):
    try:
        model_name = request.model_name
        model = get_model(model_name)
        exists = model is not None
        return {"exists": exists, "message": "Existence checked successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model_trained")
def model_trained(request: ModelRequest):
    try:
        model_name = request.model_name
        nn_model = get_nn_model(model_name)
        trained = nn_model is not None
        return {"trained": trained, "message": "trainedness checked successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/init_model")
def init_model(request: ModelRequest):
    try:
        model_name = request.model_name
        print(model_name)
        add_model(model_name)
        return {"message": "Model Initialized successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train(request: TrainRequest):
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
            nn_model = init_nn_model(features_tensor)
            nn_model = train_nn_model(nn_model, features_tensor, classes_tensor, 100, .001)
        else:
            nn_model = train_nn_model(nn_model, features_tensor, classes_tensor, 100, .001)
        print("model succesfully trained")

        add_nn_model(model_name, nn_model)

        return  {"message": "Model trained successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rec")
async def rec(request: ModelRequest):
    try:
        model_name = request.model_name
        nn_model = get_nn_model(model_name)
        # nn model must not be none
        retries = 0
        while retries < NUM_RETRIES:
            retries += 1
            current_song_id = get_random_song_id()
            current_song_features_tensor = test_song_id_to_tensor(current_song_id)
            class_prediction = predict_single_example(nn_model, current_song_features_tensor)
            if class_prediction == 1:
                return  {"message": "Rec retreived succesfully", "song_id":current_song_id}
        raise Exception(f"no matches found for the model {model_name} after {NUM_RETRIES} attempts")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/all_models")
def all_models():
    try:
        all_model_names = get_all_model_names()
        return  {"message": "Models retreived succesfully", "model_names":all_model_names}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8040, reload=True)


