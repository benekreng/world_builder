# standalone runnter
from world_builder.app import WorldBuilder
import asyncio

core = WorldBuilder()

async def main():

    world_id = await core.create_world("")

if __name__ == "__main__":
    asyncio.run(main())
