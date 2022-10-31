import asyncio
import websockets
import json


USERNAME1 = ['user1', 'user2', 'user3']
PASSWORD1 = ['helloworld', 'helloworld', 'helloworld']
JWT_TOKEN = []
GAME_ID = []


def test_game_step(token, coordinate=str()):

    async def connect():
        async with websockets.connect('ws://localhost:8765/game-step') as websocket:
            # Hard coding token and GAME_ID
            await websocket.send(
                json.dumps(
                    {
                        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIyIiwicGFzc3dvcmQiOiJoZWxsb3dvcmxkIiwiZXhwIjoxNjY4MDY1MzE2Ljg4NDY4M30.s6ESXhgMLW8azulTjcveGqBjoEPw7eO73U-_7rYsTc0', 
                        'data': {'id': '601039ca-a139-484e-8b5f-806fc2261592'},
                        'coordinate': coordinate
                    }
                )
            )
        try:
            while True:
                response = json.loads(await websocket.recv())
                break
        except:
            pass
    asyncio.run(connect())

test_game_step('', '0,0')