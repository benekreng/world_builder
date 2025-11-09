# main.py
import asyncio

class WorldState:
    def __init__(self):


class WorldBuilder:
    def __init__(self):
        self._running = False

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False 

    async def test_async(self):
        await asyncio.sleep(1)

    # creates new world from scratch
    async def create_world(self, initial_message):
        # create new world object
        # update current world to new world
        # dispatch 'new world' chain and pass it the empty world
            # potentially: stream updates to the user 
        # render new map from new world object
        # return map and world id to front end
        return

    # let the user fetch previous worlds
    async def fetch_worlds():
        # return id's of existing worlds
        return
    
    # append to world
    async def create_world(self, initial_message, world_id):
        # make sure world 'world_id' is loaded 
        # dispatch 'append/edit' chain
            # potentially: stream updates to the user 
        # render new map from world object
        # return map 
        return