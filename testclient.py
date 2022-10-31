import asyncio
import websockets
import json


USERNAME1 = ['user1', 'user2', 'user3']
PASSWORD1 = ['helloworld', 'helloworld', 'helloworld']
JWT_TOKEN = []
GAME_ID = []


def test_register(index):

    async def connect():
        async with websockets.connect('ws://localhost:8765/register') as websocket:
            await websocket.send(json.dumps({'username': USERNAME1[index], 'password': PASSWORD1[index]}))
            try:
                while True:
                    response = json.loads(await websocket.recv())
                    break
            except:
                pass
    asyncio.run(connect())

def test_login(index):

    async def connect():
        async with websockets.connect('ws://localhost:8765/login') as websocket:
            await websocket.send(json.dumps({'username': USERNAME1[index], 'password': PASSWORD1[index]}))
            try:
                while True:
                    response = json.loads(await websocket.recv())
                    JWT_TOKEN.append(response)
                    break
            except:
                pass
    asyncio.run(connect())

def test_get_feed():

    async def connect():
        async with websockets.connect('ws://localhost:8765/get-feed') as websocket:
            await websocket.send(json.dumps({'token': JWT_TOKEN[0]['data']}))
            try:
                while True:
                    response = json.loads(await websocket.recv())
                    if (
                        response.get('data')
                        and isinstance(response.get('data'), list)
                        and len(response.get('data', [])) > 0
                    ):
                        GAME_ID.append(response['data'][0]['id'])
                        break
            except:
                pass
    asyncio.run(connect())  

def test_create_game(index):

    async def connect():
        async with websockets.connect('ws://localhost:8765/create-game') as websocket:
            await websocket.send(json.dumps({'token': JWT_TOKEN[index]['data']}))
            try:
                while True:
                    response = json.loads(await websocket.recv())
                    break
            except:
                pass
    asyncio.run(connect())

def test_join_game(index):

    async def connect():
        async with websockets.connect('ws://localhost:8765/join-game') as websocket:
            await websocket.send(json.dumps({'token': JWT_TOKEN[index]['data'], 'data': {'id': GAME_ID[0]}}))
            try:
                while True:
                    response = json.loads(await websocket.recv())
                    break
            except:
                pass
    asyncio.run(connect()) 

def test_spectate_game(index):
    
    async def connect():
        async with websockets.connect('ws://localhost:8765/spectate-game') as websocket:
            await websocket.send(json.dumps({'token': JWT_TOKEN[index]['data'], 'data': {'id': GAME_ID[0]}}))
            try:
                while True:
                    response = await websocket.recv()
                    f = open('test.json', 'a+')
                    f.write(response + '\n')
                    f.close()
            except:
                pass
    asyncio.run(connect())

def test_game_step(index, coordinate=str()):

    async def connect():
        async with websockets.connect('ws://localhost:8765/game-step') as websocket:
            await websocket.send(
                json.dumps(
                    {
                        'token': JWT_TOKEN[index]['data'], 
                        'data': {'id': GAME_ID[0]},
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



test_register(0)
test_login(0)
test_create_game(0)
test_get_feed()

test_register(1)
test_login(1)
test_join_game(1)
test_spectate_game(1)

# test_game_step(0, '0,0')
# test_game_step(1, '0,1')
# test_game_step(0, '1,1')
# test_game_step(1, '1,3')
# test_game_step(0, '2,2')