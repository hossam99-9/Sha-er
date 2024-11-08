import json
import asyncio
import random

from backend.app.utils.debate import *

def normalize_char(char):
    """
    Normalize special characters in the verse.

    :param char: The character to be normalized.
    :return: The normalized character.
    """
    char = char.replace('\\n', '   ')
    char = char.replace('\n', '   ')
    char = char.replace('/n', '   ')
    char = char.replace('//n', '   ')
    char = char.replace('n/', '   ')
    char = char.replace('n//', '   ')
    char = char.replace('n\\', '   ')
    return char

async def fallback(websocket, poet_key):
    """
    Fallback function to send a random verse if the generation fails.

    :param websocket: The WebSocket connection.
    :param poet_key: The key identifying the poet.
    """
    verse = random.choice([
        "وَلِلصُبْحِ في أُفقِ السَماءِ مَرَائِمٌ يُبَدِدُها وَالليلُ لِلغَيمِ لِثامُ",
        "في حُسنِكَ ما يَستَبي الحَليمُ وَيَرتاحُ لِلَّهوِ القَديمُ",
        "في قَدِّهِ ما هُوَ في الأَغصانِ عَلى اِختِلافِ الوَضِعِ وَالمَباني",
        "في هَجْرِها ذُقْتُ المَنُونَ ولَمْ أَقُلْ أَحْبَابَنَا طَالَ اللّيَالِيَ بَعِّدُونَا",
        "يا مَن تَجَنَّبَني وَاِستَخَفَّ بِحُبِّهِ اِبكِ عَلى كُلِّ حُبٍّ فَلا اِلتِفاتُهُ",
        "بِأَبي وَأُمّي ذاكَ الغُلامُ فَإِنَّهُ خَيرُ الأَنامِ جَمالاً وَخُلقاً مُحَلَّها"
    ])
    await asyncio.sleep(2)
    for char in verse:
        await websocket.send_text(json.dumps({poet_key: char}))
        await asyncio.sleep(0.01)  # Simulate slow processing

async def send_verse(websocket, poet_key, verse):
    """
    Send the verse character by character to the WebSocket.

    :param websocket: The WebSocket connection.
    :param poet_key: The key identifying the poet.
    :param verse: The verse to be sent.
    """
    await asyncio.sleep(2)
    for char in verse:
        await websocket.send_text(json.dumps({poet_key: char}))
        await asyncio.sleep(0.01)  # Simulate slow processing

async def send_verse_stream(websocket, poet_key, verse):
    """
    Send the verse character by character to the WebSocket.

    :param websocket: The WebSocket connection.
    :param poet_key: The key identifying the poet.
    :param verse: The verse to be sent.
    :return: True if any character was sent, False otherwise.
    """
    flag_start_token = False
    anything_sent = False
    memory = ""
    for char in verse:
        if not flag_start_token:
            if char == '"' or char == 'verse' or char == '":' or char == ' "':
                memory += char
                if memory == '"verse": "':
                    flag_start_token = True
                    memory = ""
            else:
                continue
        else:
            if char.endswith('"'):
                return True
            else:
                char = normalize_char(char)
                await websocket.send_text(json.dumps({poet_key: char}))
                anything_sent = True
    return anything_sent

async def generate(websocket, prompt, generator_agent):
    """
    Generate a verse based on the prompt and send it character by character to the WebSocket.

    :param websocket: The WebSocket connection.
    :param prompt: The prompt for generating the verse.
    :param generator_agent: The agent responsible for generating the verse.
    """
    log_message(msg=f"Prompt: {prompt}", level=2)
    bait, letter = generator_agent.generate_bait_stream(prompt)

    # for char in bait:
    #     print("DEBUG:", char)

    # log_message(msg="Agent generated the bait", level=2)
    # log_message(msg=f"bait: {bait}", level=1)

    status = await send_verse_stream(websocket, "bait", bait)

    if not status:
        await fallback(websocket, "bait")
