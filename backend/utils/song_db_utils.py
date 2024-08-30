#=======================================================================#
# IMPORTS
#=======================================================================#
import random
import redis.asyncio as asyncio
import redis

from global_constants import COUNT_KEY, HASH_KEY_SONG_IDS

#=======================================================================#
# def get_song_count(): Gets the number of songs in the db based on
# the kv pair at 'COUNT_KEY'
#=======================================================================#
def get_song_count():
    r = redis.Redis(host='localhost',port=6379,db=1)

    db_song_count = int(r.get(COUNT_KEY))
    if db_song_count is None:
        raise Exception("unable to get db song counts")
    return int(r.get(COUNT_KEY))

#=======================================================================#
# async def get_random_song_ids(num_songs): returns a list of random song
# ids fetched from the database
#=======================================================================#
async def get_random_song_ids(num_songs):
    r = await asyncio.from_url("redis://localhost", db=1)
    db_song_count = get_song_count()

    random_indices = [str(random.randint(0, db_song_count-1)) for _ in range(num_songs)]

    result_as_bytes = await r.hmget(HASH_KEY_SONG_IDS, *random_indices) # the * syntaxa unpacks the list to apply as arguments
    result = [item.decode('utf-8') if item else None for item in result_as_bytes]
    await r.close()

    return result
