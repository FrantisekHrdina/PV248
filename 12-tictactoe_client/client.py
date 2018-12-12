#!/usr/bin/env python3

import asyncio
import json
import sys
import aiohttp


def get_round(board):
    last_round = 0

    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j] != 0:
                last_round += 1

    return last_round


def print_board(board):
    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j] == 1:
                print('x', end='')
            elif board[i][j] == 2:
                print('o', end='')
            else:
                print('_', end='')
        print()


async def list_games():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://' + HOST + ':' + PORT + '/list') as response:
            games = json.loads(await response.text())
            return games, len(games)


async def start(name):
    if name is None:
        game_name = ''
    else:
        game_name = str(name)

    async with aiohttp.ClientSession() as session:
        async with session.get('http://' + HOST + ':' + PORT + '/start?name=' + game_name) as response:
            start_response = json.loads(await response.text())
            return start_response['id']


async def status(game_id):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://' + HOST + ':' + PORT + '/status?game=' + str(game_id)) as response:
            status_response = json.loads(await response.text())
            return status_response


async def play(game_id, player, x, y):
    params = 'game=' + str(game_id) + '&player=' + str(player) + '&x=' + str(x) + '&y=' + str(y)

    async with aiohttp.ClientSession() as session:
        async with session.get('http://' + HOST + ':' + PORT + '/play?' + params) as response:
            play_response = json.loads(await response.text())
            return play_response


def print_info(last_round, current_round, board, player, next):
    if player == 1:
        mark = 'x'
    else:
        mark = 'o'

    if last_round != current_round:
        print_board(board)
        if player == next:
            print('Your turn ({0})'.format(mark))
        else:
            print('Waiting for oponent')

    return current_round


def print_winner(player, winner):
    if player == winner:
        print('you win')
    elif winner == 0:
        print('draw')
    else:
        print('you lose')


@asyncio.coroutine
async def main():
    global HOST
    HOST = sys.argv[1]
    global PORT
    PORT = sys.argv[2]

    games_list, games_count = await list_games()

    if games_count != 0:
        print('these games are available')
        print(games_list)
    else:
        print('no game available, start new one')

    print('Set the id of game you want to play or new for starting new')

    while True:
        game_id = input()
        if game_id.startswith('new'):
            player = 1

            splitted = game_id.split(" ")
            if splitted.__len__() == 1:
                game_id = await start(None)
            else:
                game_id = await start(' '.join(map(str, splitted[1:])))

            print(game_id)
            break
        else:
            try:
                game_id = int(game_id)
            except:
                print('game id must be digit')
                print('Set the id of game you want to play or new for starting new')
                continue

            if game_id >= games_count:
                print('no such game with this id')
                print('Set the id of game you want to play or new for starting new')
                continue

            player = 2
            break

    round_number = -1
    while True:
        winner = None

        status_response = await status(game_id)
        if status_response.get('winner'):
            winner = status_response['winner']
            print_winner(player, winner)
            return
        board = status_response['board']

        current_round = get_round(board)
        round_number = print_info(round_number, current_round, board, player, status_response['next'])

        if player == status_response['next']:
            print('Set coordinates x and y:')
            coordinates = input()
            coordinates = coordinates.split(' ')

            x = coordinates[0]
            y = coordinates[1]
            play_response = await play(game_id, player, x, y)

            if play_response['status'] == 'bad':
                print('invalid input')
        await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

