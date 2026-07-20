# import asyncio
# import websockets
# import json

# async def test():
#     async with websockets.connect("ws://localhost:8765") as websocket:
#         print("Connected to game server")
        
#         # Receive initial board state
#         msg = await websocket.recv()
#         data = json.loads(msg)
#         print(f"\nInitial board state received:")
#         print(f"  Type: {data['type']}")
#         print(f"  Game over: {data['game_over']}")
#         print(f"  Board size: {len(data['board'])}x{len(data['board'][0])}")
        
#         # Receive a few more updates
#         print("\nReceiving board updates...")
#         for i in range(3):
#             msg = await websocket.recv()
#             data = json.loads(msg)
#             print(f"  Update {i+1}: {data['type']}")
        
#         print("\nTest passed! Server is broadcasting board state.")

# asyncio.run(test())

import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("Connected to game server")
        
        # Receive initial board state
        msg = await websocket.recv()
        data = json.loads(msg)
        print(f"\nInitial board state received:")
        print(f"  Type: {data['type']}")
        print(f"  Room ID: {data['room_id']}")
        print(f"  Game over: {data['game_over']}")
        print(f"  Board size: {len(data['board'])}x{len(data['board'][0])}")
        
        # Verify room_id is "default"
        assert data['room_id'] == "default", f"Expected room_id='default', got '{data['room_id']}'"
        
        # Receive a few more updates
        print("\nReceiving board updates...")
        for i in range(3):
            msg = await websocket.recv()
            data = json.loads(msg)
            print(f"  Update {i+1}: room_id={data['room_id']}, type={data['type']}")
            assert data['room_id'] == "default"
        
        print("\n✓ Test passed! RoomsManager is working correctly.")
        print("  - Server uses RoomsManager with 'default' room")
        print("  - Board state includes room_id")
        print("  - Multiple updates received successfully")

asyncio.run(test())
