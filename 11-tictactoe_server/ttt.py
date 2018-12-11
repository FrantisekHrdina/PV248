#!/usr/bin/env python3
import asyncio
import sys
import ttt_game
import json

from aiohttp import web


@asyncio.coroutine
async def start_handler(request):
    if 'name' not in request.query.keys():
        name = ''
        # return web.Response(status=500, text='bad request, missing key name')
    else:
        name = request.query['name']

    # if name == '':
    #     return web.Response(status=500, text='bad request, empty name not allowed')

    new_game = ttt_game.Game()
    new_game.name = name
    new_game.id = games.__len__()

    games.append(new_game)

    response = {}
    response['id'] = new_game.id

    # Testing
    # if new_game.id == 0:
    #     await asyncio.sleep(10)

    return web.Response(status=200, text=json.dumps(response, indent=4))


@asyncio.coroutine
async def status_handler(request):
    response = {}
    if 'game' not in request.query.keys():
        return web.Response(status=400)


    try:
        game_id = int(request.query['game'])
    except ValueError:
        #response['message'] = 'game must be digit'
        return web.Response(status=400)

    if game_id >= games.__len__():
        # response['status'] = 'bad'
        # response['message'] = 'bad request, game with this id does not exist'
        return web.Response(status=404)

    game = games[int(game_id)]

    if game.winner is None:
        response['board'] = game.board
        response['next'] = game.next
    else:
        response['winner'] = game.winner

    return web.Response(status=200, text=json.dumps(response, indent=4))


@asyncio.coroutine
async def play_handler(request):
    response = {}
    if not set(['player', 'game', 'x', 'y']).issubset(request.query.keys()):
        response['status'] = 'bad'
        response['message'] = 'some of mandatory keys (player, game, x, y)  are missing'
        return web.Response(status=400, text=json.dumps(response, indent=4))

    try:
        player = int(request.query['player'])
        game_id = int(request.query['game'])
        x = int(request.query['x'])
        y = int(request.query['y'])
    except ValueError:
        response['status'] = 'bad'
        response['message'] = 'params values must be digits'
        return web.Response(status=400, text=json.dumps(response, indent=4))

    if x < 0 or x >= ttt_game.HEIGHT or y < 0 or y >= ttt_game.WIDTH:
        response['status'] = 'bad'
        response['message'] = 'x and y must be in 0 or 1 or 2'
        return web.Response(status=422, text=json.dumps(response, indent=4))

    if game_id >= games.__len__():
        response['status'] = 'bad'
        response['message'] = 'game with this id does not exist'
        return web.Response(status=404, text=json.dumps(response, indent=4))

    if player != 1 and player != 2:
        response['status'] = 'bad'
        response['message'] = 'player must be 1 or 2'
        return web.Response(status=422, text=json.dumps(response, indent=4))

    game = games[game_id]

    if game.winner is not None:
        response['status'] = 'bad'
        response['message'] = 'game was already finished'
        return web.Response(status=403, text=json.dumps(response, indent=4))

    if player != game.next:
        response['status'] = 'bad'
        response['message'] = 'it is not your turn yet'
        return web.Response(status=403, text=json.dumps(response, indent=4))

    if game.board[x][y] != 0:
        response['status'] = 'bad'
        response['message'] = 'bad request, box is already taken'
        return web.Response(status=403, text=json.dumps(response, indent=4))

    response['status'] = 'ok'
    game.board[x][y] = player

    game.set_winner()

    if player == 1:
        game.next = 2
    else:
        game.next = 1

    game.print_log()

    return web.Response(status=200, text=json.dumps(response, indent=4))


@asyncio.coroutine
async def list_handler(request):
    games_list = []

    for game in games:
        if not game.are_all_boxes_filled():
            tmp_game = {}
            tmp_game['id'] = game.id
            tmp_game['name'] = game.name
            games_list.append(tmp_game)

    return web.Response(status=200, text=json.dumps(games_list, indent=4))


@asyncio.coroutine
async def bad_handler(request):
    if request.method == 'POST':
        return web.Response(status=405)
    return web.Response(status=404)

def main():
    # logging.basicConfig(level=logging.DEBUG)
    global PORT
    PORT = int(sys.argv[1])

    global games
    games = []

    my_server = web.Application()
    my_server.router.add_route('GET', '/start{tail:.*}', start_handler)
    my_server.router.add_route('GET', '/status{tail:.*}', status_handler)
    my_server.router.add_route('GET', '/play{tail:.*}', play_handler)
    my_server.router.add_route('GET', '/list{tail:.*}', list_handler)
    my_server.router.add_route('GET', '/{tail:.*}', bad_handler)
    my_server.router.add_route('POST', '/{tail:.*}', bad_handler)
    web.run_app(my_server, host='localhost', port=PORT)


if __name__ == '__main__':
    main()