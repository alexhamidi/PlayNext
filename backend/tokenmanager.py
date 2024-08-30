import requests
import time
from fastapi import HTTPException

#=======================================================================#
# TokenManager class handles all functionalities for retriving and
# Updating tokens. (issue: no user data)
#=======================================================================#

class TokenManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expiry = 0

    def get_token(self):
        if self.token and time.time() < self.token_expiry:
            return self.token

        data = {
            "grant_type:": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post("https://accounts.spotify.com/api/token", data = data)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to obtain Spotify token")

        token_info = response.json()

        self.token = token_info['access_token']
        self.token_expiry = time.time() + token_info['expires_in'] - 300

        return self.token
