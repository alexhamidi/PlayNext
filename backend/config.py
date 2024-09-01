from dotenv import load_dotenv
import os
load_dotenv()

#SPOTIFY AUTH
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

#SPOTIFY REQS
AUDIO_ANALYSIS_URL = "https://api.spotify.com/v1/audio-analysis/"

#RATE LIMITING
MAX_API_RETRIES_PER_SONG = 6
RATE_LIMIT_DELAY = 5

#ML
NUM_RETRIES_PER_PREDICTION_BATCH = 8
POSITIVE_THRESHOLD = .5
REC_BATCH_SIZE = 20
NUM_CLASSES = 2
NUM_FEATURES = 40000
MAX_FEATURE_EXAMPLES = 1000


#DB
HASH_KEY_SONG_IDS = "song_ids"
COUNT_KEY = "num_song_ids"

#PROCESSING
TRACK_URL = 'https://open.spotify.com/track'
TRACK_PATTERN = r"^https://open\.spotify\.com/track/([a-zA-Z0-9]{22})$"
