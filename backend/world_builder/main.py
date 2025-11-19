# standalone runnter
from world_builder.app import WorldBuilder

import asyncio
from pathlib import Path

core = WorldBuilder()

EXAMPLE_PROMPT_DIR = (Path(__file__).parent / 'test/example_user_prompts')
EXAMPLE_PROMPT = (EXAMPLE_PROMPT_DIR / "ex_1.prompt").read_text()

async def main():
    world_id = await core.create_world(EXAMPLE_PROMPT)

if __name__ == "__main__":
    asyncio.run(main())
