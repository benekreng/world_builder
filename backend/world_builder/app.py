# main.py
import asyncio

class WorldBuilder:
    def __init__(self):
        self._running = False

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False 

    async def test_async(self):
        await asyncio.sleep(1)
