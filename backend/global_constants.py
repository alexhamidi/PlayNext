from dotenv import load_dotenv
import os
load_dotenv()

#SPOTIFY AUTH
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

#SPOTIFY REQS
AUDIO_URL = "https://api.spotify.com/v1/audio-analysis/"
KEYS_TO_USE = ['duration', 'loudness', 'tempo', 'time_signature', 'key', 'mode']

#ML
NUM_RETRIES_PER_BATCH = 10
POSITIVE_THRESHOLD = .5
REC_BATCH_SIZE = 20
NUM_CLASSES = 2
NUM_FEATURES = len(KEYS_TO_USE)

#DB
HASH_KEY_SONG_IDS = "song_ids"
COUNT_KEY = "num_song_ids"

#PROCESSING
TRACK_URL = 'https://open.spotify.com/track'
TRACK_PATTERN = r"^https://open\.spotify\.com/track/([a-zA-Z0-9]{22})$"
