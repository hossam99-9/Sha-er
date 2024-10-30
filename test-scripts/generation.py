import asyncio
import websockets
import json

async def test_poetry_generation(prompt: str):
    uri = "ws://10.100.20.148:8001/ws/generate"
    async with websockets.connect(uri + f"?prompt={prompt}") as websocket:
        try:
            bait = ''  # Initialize an empty string to build the verse
            while True:
                response = await websocket.recv()  # Receive each character from the server
                data = json.loads(response)
                
                # Append the character to the 'bait' if it exists
                if 'bait' in data:
                    bait += data['bait']  # Append each character as it comes
                
                # Optionally, print the verse progressively
                print(f"\r{bait}", end='', flush=True)
                
        except websockets.exceptions.ConnectionClosedOK:
            print("\nConnection closed")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    prompt = "أريد بيت شعر عن الحب علي طريقة الشاعر أحمد شوقي ينتهي بقافية النون"
    asyncio.run(test_poetry_generation(prompt))