import datetime
import json

import jwt
import asyncio
import websockets


class Server:

    def __init__(self, host='localhost', port='8765'):
        self.CONNECTED = []
        self.host = host
        self.port = port
        self.accounts = []
        # Game IDs could be stored in hashmap with details
        # This will help in getting game information quickly. 
        self.feed = []

    def key(self):
        return 'repostreet'

    def start(self):
        return websockets.serve(self.handler, self.host, self.port)

    def get_account(self, token):
        decoded = jwt.decode(token, key=self.key(), algorithms=['HS256'])
        epoch = datetime.datetime.fromtimestamp(decoded['exp'])
        if datetime.datetime.now() < epoch:
            return decoded, True
        return dict(), False

    def get_left_digonal(self, matrix, username):
        found = True
        for index9 in range(3):
            index10 = index9
            if matrix[index9][index10] != username:
                found = False
        return found

    def get_right_digonal(self, matrix, username):
        found = True
        for index9 in range(3):
            index10 = 2 - index9
            if matrix[index9][index10] != username:
                found = False
        return found

    def get_vertical(self, matrix, username):
        for index7 in range(3):
            found = False
            for index8 in range(3):
                if matrix[index8][index7] == username:
                    found = True
                else:
                    found = False
                    break
            if found:
                return found
        return found

    def get_horizontal(self, matrix, username):
        for index5 in range(3):
            found = False
            for index6 in range(3):
                if matrix[index5][index6] == username:
                    found = True
                else:
                    found = False
                    break
            if found:
                return found
        return found

    def won(self, player, steps):
        matrix = self.get_matrix(steps)
        won = False
        if self.get_horizontal(matrix, player):
            won = True
        elif self.get_vertical(matrix, player):
            won = True
        elif self.get_left_digonal(matrix, player):
            won = True
        elif self.get_right_digonal(matrix, player):
            won = True
        return won

    def get_matrix(self, steps):
        matrix = [[-1 for j in range(3)] for i in range(3)]
        won = False
        for step in steps:
            coord1 = step['coordinate'][0]
            coord2 = step['coordinate'][1]
            matrix[coord1][coord2] = step['username']
        return matrix


    async def handler(self, websocket, path):
        if 'login' in path:
            async for message in websocket:
                message = json.loads(message)
                username = message.get('username')
                password = message.get('password')

                if not username in [i['username'] for i in self.accounts]:
                    await websocket.send(json.dumps({'status': False, 'message': 'Username is not valid'}))
                else:
                    userobject = None
                    for i, v in enumerate(self.accounts):  
                        if v['username'] == username and v['password'] == password:
                            userobject = v
                            expiry = datetime.datetime.now() + datetime.timedelta(days=10)
                            expiry = expiry.timestamp()
                            v['exp'] = expiry
                            token = jwt.encode(payload=v, key=self.key())
                            await websocket.send(json.dumps({'status': True, 'message': 'Login successful', 'data':  token}))
                    if not userobject:
                        await websocket.send(json.dumps({'status': False, 'message': 'Password is invalid'}))

        elif 'register' in path:
            async for  message in websocket:
                message =  json.loads(message)
                username = message['username']
                password = message['password']

                usernames = [i['username'] for i in self.accounts]
                if username in usernames:
                    await websocket.send(json.dumps({'status': False, 'message': 'Username already exist'}))
                else:
                    self.accounts.append(message)
                    await websocket.send(json.dumps({'status': True, 'message': 'Registration successful'}))


        elif 'get-feed' in path:
            async for message in websocket:
                message = json.loads(message)
                account, status = self.get_account(message['token'])
                if status == True:
                    feed = [i for i in self.feed]
                    feed.reverse()
                    feed = feed[:20]
                    self.CONNECTED.append(websocket)
                    await websocket.send(json.dumps({'status': True, 'message': 'Connected to feed', 'data': feed}))
                else:
                    await websocket.send(json.dumps({'status': False, 'message': 'Invalid credentials'}))


        elif 'create-game' in path:
            async for message in websocket:
                message = json.loads(message)
                account, status = self.get_account(message['token'])
                import uuid
                if status:
                    game = dict(
                        id=str(uuid.uuid4()),
                        player_one=account['username'],
                        player_two=str(),
                        steps=list(),
                        winner=str(),
                        connection=list()
                    )
                    self.feed.append(game)
                    if self.CONNECTED:
                        await asyncio.wait([websocket.send(json.dumps(game)) for i in self.CONNECTED])
                    await websocket.send(json.dumps({'status': False, 'message': 'Game created', 'data': game}))
                else:
                    await asyncio.send(json.dumps({'status': False, 'message': 'Invalid credentials'}))

        elif 'join-game' in path:
            async for message in websocket:
                message = json.loads(message)
                account, status = self.get_account(message['token'])

                if status:
                    game = message['data']['id']
                    valid = False
                    for index1, value1 in enumerate(self.feed):
                        if value1['id'] == game:
                            ERROR_MESSAGE = 'You have alreaady joined'
                            if value1['player_one'] and value1['player_two']:
                                await websocket.send(json.dumps({'status': False, 'message': 'Please create a new game'})) 
                            elif value1['player_one'] == account['username']:
                                await websocket.send(json.dumps({'status': False, 'message': ERROR_MESSAGE}))
                            elif value1['player_two'] == account['username']:
                                await websocket.send(json.dumps({'status': False, 'message': ERROR_MESSAGE}))
                            else:
                                self.feed[index1] = dict(
                                    id=value1['id'],
                                    player_one=value1['player_one'],
                                    player_two=account['username'],
                                    steps=[], 
                                    winner=str(),
                                    connection=[]
                                )
                                await websocket.send(json.dumps({'status': False, 'message': 'Game joined'}))
                else:
                    await websocket.send(json.dumps({'status': False, 'message': 'Unauthorized.'}))

        elif 'spectate-game' in path:
            async for message in websocket:
                message = json.loads(message)
                account, status = self.get_account(message['token'])

                if status:
                    gameID = message['data']['id']
                    game_instance = dict()

                    for index3, value3 in enumerate(self.feed):
                        if value3['id'] == gameID:
                            if value3['player_one'] == account['username'] or value3['player_two'] == account['username']:
                                connections = value3['connection']
                                connections.append(
                                    {
                                        'username': account['username'],
                                        'socket': websocket 
                                    }
                                )
                                GAME_DATA = dict(
                                    id=value3['id'],
                                    player_one=value3['player_one'],
                                    player_two=value3['player_two'],
                                    steps=value3['steps'],
                                    winner=value3['winner'],
                                    connection=connections
                                )
                                self.feed[index3] = GAME_DATA
                                await websocket.send(json.dumps({'status': True, 'message': 'Game joined'}))
                else:
                    await websocket.send(json.loads({'status': False, 'message': 'Unauthorized'}))

        elif 'game-step' in path:
            async for message in websocket:
                message = json.loads(message)
                account, status = self.get_account(message['token'])

                if status:
                    game = message['data']['id']
                    game_instance = dict()

                    for index2, value2 in enumerate(self.feed):
                        if value2['id'] == game:
                            game_instance = value2

                    if (
                        game_instance.get('id')
                        and (account['username'] == game_instance['player_one'] or account['username'] == game_instance['player_two'])
                        ):
                        coordinate = message['coordinate']
                        game_stat, status = self.game_status(account, game_instance, coordinate)
                        game_sockets = [i['socket'] for i in value2['connection']]

                        if status == 'MATCH_OVER':
                            await asyncio.wait([i.send(json.dumps({'status': False, 'message': 'DRAW', 'game': self.get_matrix(game_stat)})) for i in game_sockets])
                        elif status == 'WON':
                            await asyncio.wait([i.send(json.dumps({'status': True, 'message': 'WON', 'game': self.get_matrix(game_stat)})) for i in game_sockets])
                        elif status == 'STEPPED':
                            await asyncio.wait([i.send(json.dumps({'status': True, 'message': 'STEPPED','game': self.get_matrix(game_stat)})) for i in game_sockets])
                        elif status == 'WAIT':
                            await asyncio.wait([i.send(json.dumps({'status': False, 'message': 'Waiting for next player', 'game': self.get_matrix(game_stat)})) for i in game_sockets])
                    else:
                        await websocket.send(json.dumps({'status': False, 'message': 'Game not found'}))
                else:
                    await websocket.send(json.dumps({'status': False, 'message': 'Unauthorized'}))

    def game_status(self, account, game_instance, coordinate):
        gameID = game_instance['id']
        status = None
        for index4, value4 in enumerate(self.feed):
            if value4['id'] == gameID:
                player_1 = self.won(value4['player_one'], value4['steps'])
                player_2 = self.won(value4['player_two'], value4['steps'])
                if len(value4['steps']) >= 9 and not (player_1 or player_two):
                    return value4['steps'], 'GAME_OVER'
                elif len(value4['steps']) < 1:
                    step = list(map(int, coordinate.split(',')))
                    value4['steps'].append(
                        {
                            'username': account['username'], 
                            'coordinate': step
                        }
                    )
                    game = dict(
                        id= value4['id'],
                        player_one=value4['player_one'],
                        player_two=value4['player_two'],
                        connection=value4['connection'],
                        steps=value4['steps'],
                        winner=str()
                    )
                    self.feed[index4] = game
                    return value4['steps'], 'STEPPED'
                elif len(value4['steps']) > 1:
                    last_step = value4['steps'][-1]
                    if last_step['username'] == account['username']:
                        return value4, 'WAIT'
                    step = list(map(int, coordinate.split(',')))
                    value4['step'].append(
                        {
                            'username': account['username'], 
                            'coordinate': step
                        }
                    )
                    game = dict(
                        id= value4['id'],
                        player_one=value4['player_one'],
                        player_two=value4['player_two'],
                        connection=value4['connection'],
                        steps=value4['step'],
                        winner=str()
                    )
                    self.feed[index4] = game
                    player_1 = self.won(value4['player_one'], value4['steps'])
                    player_2 = self.won(value4['player_two'], value4['steps'])

                    if player_1:
                        return value4['steps'], 'Player 1 WON'
                    elif player_2:
                        return value4['steps'], 'Player 2 WON'
                    else:
                        return value4['steps'], 'STEPPED' 

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = '8765'

    server = Server(host=HOST, port=PORT)
    server_instance = server.start()
    asyncio.get_event_loop().run_until_complete(server_instance)
    asyncio.get_event_loop().run_forever()
