import requests
import time
from fastapi import HTTPException
from config import CLIENT_ID, CLIENT_SECRET

class TokenManager:
    _instance = None # class variable that holds the instaance of the class

    def __new__(cls): # new is a special method that creates a new instance of the class. (TokenManager)
        if cls._instance is None: # if there is not yet an instance.
            cls._instance = super(TokenManager, cls).__new__(cls) # call the new method of this class, which is general 'object' (just makes a new object
            # set all values of the instance
            cls._instance.client_id = None
            cls._instance.client_secret = None
            cls._instance.token = None
            cls._instance.token_expiry = 0
        return cls._instance

    def initialize(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self):
        if not self.client_id or not self.client_secret:
            raise ValueError("TokenManager not initialized. Call initialize() first.")

        if self.token and time.time() < self.token_expiry:
            return self.token

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post("https://accounts.spotify.com/api/token", data=data)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to obtain Spotify token")

        token_info = response.json()
        self.token = token_info["access_token"]
        self.token_expiry = time.time() + token_info["expires_in"] - 300  # Refresh 5 minutes before expiry

        return self.token

token_manager = TokenManager()


def main():
    token_manager.initialize(CLIENT_ID, CLIENT_SECRET)
    token = token_manager.get_token()
    print(token)

    return 0

if __name__ == "__main__":
    main()
