import asyncio
import websockets
import json
import sys
import urllib.parse

async def connect_websocket(prompt):
    # Encode the prompt for use in a URL
    encoded_prompt = urllib.parse.quote(prompt)
    uri = f"ws://localhost:8002/ws/generate?prompt={encoded_prompt}"

    try:
        async with websockets.connect(uri, timeout=30) as websocket:
            print(f"Connected to {uri}")

            while True:
                try:
                    # Receive data from the server
                    response = await asyncio.wait_for(websocket.recv(), timeout=60)
                    data = json.loads(response)
                    
                    # Process the server response
                    if "bait" in data:
                        print(data["bait"], end='', flush=True)

                except asyncio.TimeoutError:
                    print("\nTimeout while waiting for server response. The server may be processing a long request.")
                    print("Do you want to continue waiting? (y/n)")
                    if input().lower() != 'y':
                        break
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket error: {e}")
    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running and the address is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def main():
    prompt = "أريد بيت شعر علي طريقة أحمد شوقي عن الحب ينتهي بقافية النون"

    try:
        await connect_websocket(prompt)
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    if sys.version_info[0] == 3 and sys.version_info[1] >= 7:
        asyncio.run(main())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())