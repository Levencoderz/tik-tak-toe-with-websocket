import asyncio
import websockets
import json


USERNAME1 = 'samim'
PASSWORD1 = 'helloworld'


def test_register():

	async def connect():
		async with websockets.connect('ws://localhost:8765/register') as websocket:
			await websocket.send(json.dumps({'username': USERNAME1, 'password': PASSWORD1}))
			try:
				while True:
					response = json.loads(await websocket.recv())
					print(response)
					break
			except:
				pass

	asyncio.run(connect())

def test_login():

	async def connect():
		async with websockets.connect('ws://localhost:8765/login') as websocket:
			await websocket.send(json.dumps({'username': USERNAME1, 'password': PASSWORD1}))
			try:
				while True:
					response = json.loads(await websocket.recv())
					break
			except:
				pass
	asyncio.run(connect())

def test_game_client(token):

	async def connect():
		async with websockets.connect('ws://localhost:8765/create-game'):
			await websocket.send(json.dumps({'token': token['data']}))
			try:
				while True:
					response = json.loads(await websocket.recv())
			except:
				pass

def test_create_game(token):

	async def connect():
		async with websockets.connect('ws://localhost:8765/login') as websocket:
			await websocket.send(json.dumps({'username': USERNAME1, 'password': PASSWORD1}))
			try:
				while True:
					response = json.loads(await websocket.recv())
					asyncio.run(test_game_client(token))
					break
			except:
				pass
	asyncio.run(connect())	
