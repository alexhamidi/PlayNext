from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils import * 
from ml import * 
from torch import *


app = FastAPI()

origins = [
  'http://localhost:8080'
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class Request(BaseModel):
    gooddata: str
    baddata: str

@app.post("/predict")
async def predict(request: Request):
    try:
        gooddata = request.gooddata
        baddata = request.baddata

        goodids, badids = raw_input_to_song_ids(gooddata, baddata)

        train_data = await song_ids_to_feature_tensor(goodids, badids)


        # testing_song_ids = get_all_artist_songs(input_song_ids)
        # test_data = song_ids_to_feature_tensor(testing_song_ids)

        parameters = train(train_data)
        # results = predict(parameters, test_data)

        return "Hello"
    except Exception as e:
        print(e) 
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn  

    uvicorn.run("app:app", host="localhost", port=8040, reload=True)
