import json
import asyncio

from backend.app.utils.debate import *

async def send_verse(websocket, poet_key, verse):
    for char in verse:
        await websocket.send_text(json.dumps({poet_key: char}))
        await asyncio.sleep(0.1)  # Simulate slow processing


async def generate(websocket,
                   prompt,
                   generator_agent
                   ):

  log_message(msg=f"Prompt: {prompt}", level=2)
  bait, letter = generator_agent.generate_bait(prompt)

  log_message(msg="Agent generated the bait", level=2)
  log_message(msg=f"bait: {bait}", level=1)

  await send_verse(websocket, "bait", bait)