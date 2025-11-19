# main.py
import asyncio
from .router import LLMService 
import random

from langchain_core.output_parsers import PydanticOutputParser
from .models import FeatureGraph 

# class WorldState:
#     def __init__(self):

class WorldBuilder:
    def __init__(self):
        self._running = False
        self.r = LLMService()
        self.r.get_model("openai/gpt-5-mini")
        self.current_world = -1

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False 

    async def test_async(self):
        await asyncio.sleep(1)

    # creates new world from scratch
    async def create_world(self, initial_message):
        new_world = World()
        self.current_world_id = new_world.id
        # try:
        #     await self._process_world(new_world, initial_message)
        # except Exception as e: 
        #     print(f"Processing world failed {e}")
        
        pydantic_parser = PydanticOutputParser(pydantic_object=FeatureGraph)
        format_instructions = pydantic_parser.get_format_instructions()
        print(format_instructions)
        
        # store world timestamp
        return new_world.id
    
    async def _process_world_start(self, world):

        return 0

    async def fetch_worlds():
        return
    
    async def append_to_world(self, initial_message, world_id):
        return

class World:
    def __init__(self):
        self.id = random.getrandbits(64)
        self._entities_hist = [{}]
        self._world_state_hist = [""]
    
    def rewind(self):
        del self._entities_hist[:-1]
        del self._world_state_hist[:-1]
    
    def get_entities_obj(self, t=0):
        # get entities as timestamp t
        t_idx = (len_(self.entities_hist) - 1) - t
        return self._entities_hist[t_idx] 
    
    def get_world_state_str(self, t=0):
        # get entities as timestamp t
        t_idx = (len_(self._world_state_hist) - 1) - t
        return self._world_state_hist[t_idx] 

    def update(self, entities, world_state):
        if not isinstance(entities, obj):
            raise TypeError("Entities is not of type object!")
        self._entities_hist.append(entities)

        if not isinstance(world_state, str):
            raise TypeError("World_state is not of type object!")
        self._world_state_hist.append(world_state)