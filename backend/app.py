from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ml import *
from utils.db_utils import *
from utils.processing_utils import *
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

'''
example: initial insert
user = User(**{
    "user_id": user_id,
    "model": null"
})

example: getting the user
user = User.find(
    User.user_id == user_id
).all()

can use
user.model

and use user.save()
'''

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
async def train_endpoint(request: TrainRequest):
    try:
        print("Starting data processing...")
        model_name = request.model_name
        positive_data = request.positive_examples
        negative_data = request.negative_examples

        positive_example_ids = raw_input_to_song_ids(positive_data)
        negative_example_ids = raw_input_to_song_ids(negative_data)

        example_ids_flagged = [(positive_example, 1) for positive_example in positive_example_ids] + [(negative_example, 0) for negative_example in negative_example_ids]
        features_tensor, classes_tensor = await song_ids_to_tensors(example_ids_flagged)

        nn_model = get_nn_model(model_name)

        if (nn_model is None):
            nn_model = init_nn_model(features_tensor)
            nn_model = train_nn_model(nn_model, features_tensor, classes_tensor, 100, .001)
        else:
            nn_model = train_nn_model(nn_model, features_tensor, classes_tensor, 100, .001)

        add_nn_model(nn_model, model_name)

        return  {"message": "Model trained successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8040, reload=True)


'''
@app.get("/rec")
async def train_endpoint(request: ModelRequest):
    try:
        user_id = request.user_id
        model = r.get(user_id)
        if (model is None):
            return "error: need to train the model first"

        cached_ids = redis.cached_ids

        while (True):
            current_song_id = random.choice(cached_ids)
            current_song_features = features.current_song_id
            class_prediction = predict_single_example(model, current_song_features)
            if class_prediction == 1:
                return current_song_id

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
'''
