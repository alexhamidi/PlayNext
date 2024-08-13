from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.utils import * 
from backend.ml import * 

import uvicorn

app = FastAPI()

origins = [
    "http://127.0.0.1:8080"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class Request(BaseModel):
    text: str

@app.post("/predict")
async def predict(request: Request):
    try:
        input = request.text

        input_song_ids = raw_input_to_song_ids(input)
        train_data = song_ids_to_feature_tensor(input_song_ids)

        testing_song_ids = get_all_artist_songs(input_song_ids)
        test_data = song_ids_to_feature_tensor(testing_song_ids)

        parameters = train(train_data)
        results = predict(parameters, test_data)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8040)