import asyncio
import websockets
import json
import sys

async def connect_websocket(poet1, poet2, topics):
    uri = "ws://localhost:8002/ws/battle"  # No query parameters in the URI

    try:
        async with websockets.connect(uri, timeout=30) as websocket:
            print(f"Connected to {uri}")
            
            # Prepare the data to be sent as JSON
            initial_data = {
                "poet1": poet1,
                "poet2": poet2,
                "topics": topics
            }
            
            # Send the initial data to the server
            await websocket.send(json.dumps(initial_data))
            print(f"Sent poets and topics: {initial_data}")

            while True:
                try:
                    # Receive data from the server
                    response = await asyncio.wait_for(websocket.recv(), timeout=60)
                    data = json.loads(response)
                    
                    # Process the server response
                    if "poet1" in data:
                        print(data["poet1"], end='', flush=True)
                    elif "poet2" in data:
                        print("\n")
                        print(data["poet2"], end='', flush=True)
                    elif "Judge" in data:
                        print(data["Judge"], end='\n', flush=True)
                    else:
                        print(f"Received: {data}")
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
    poet1 = "أحمد شوقي"
    poet2 = "خليل مطران"
    topics = ["حزين", "وطني", "رومانسي"]

    try:
        await connect_websocket(poet1, poet2, topics)
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