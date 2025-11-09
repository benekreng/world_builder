# standalone runnter
from world_builder.app import WorldBuilder
import asyncio

core = WorldBuilder()

async def main():
    await core.test_async()
    print("cool")

if __name__ == "__main__":
    asyncio.run(main())
