#!/usr/bin/env python3
import os
import sys

import aiohttp
import asyncio
import subprocess
from subprocess import PIPE

from aiohttp import web


@asyncio.coroutine
async def handler(request):
    headers = {"Content-Type": "text/plain; charset=utf-8"}

    if not os.path.exists(DIR + request.url.path):
        return web.Response(status=404, headers=headers)

    if os.path.isdir(DIR + request.url.path):
        return web.Response(status=403, headers=headers)


    if request.headers.get("Authorization") is None:
        auth_type = ''
    else:
        auth_type = request.headers.get("Authorization")

    if request.content_type is None:
        content_type = ''
    else:
        content_type = request.content_type

    os.putenv('AUTH_TYPE', auth_type)
    # os.putenv('CONTENT_LENGTH', )
    os.putenv('CONTENT_TYPE', content_type)
    os.putenv('GATEWAY_INTERFACE', 'CGI/1.1')
    os.putenv('PATH_INFO', request.url.raw_path)
    os.putenv('QUERY_STRING', request.query_string)
    os.putenv('REMOTE_ADDR', '127.0.0.1')
    os.putenv("REQUEST_METHOD", request.method)
    os.putenv("SERVER_NAME", '127.0.0.1')
    os.putenv("SERVER_PORT", str(PORT))
    os.putenv("SERVER_PROTOCOL", 'HTTP/1.1')
    software = 'Python ' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2])

    os.putenv("SCRIPT_NAME", os.path.basename(str(request.url)))
    os.putenv("SERVER_SOFTWARE", software)

    content_length = 0
    if request.method == 'POST' and request.content_length is not None:

        content_length = request.content_length

    os.putenv('CONTENT_LENGTH', str(content_length))

    content = 0
    if content_length > 0:
        content = await request.text()

    # Not mandatory variables
    # os.putenv('REMOTE_HOST', )
    # os.putenv("REMOTE_IDENT", )
    # os.putenv("REMOTE_USER",)
    # os.putenv('PATH_TRANSLATED', )

    script_path = request.url.path

    if script_path.endswith('.cgi'):
        p = await asyncio.create_subprocess_shell(DIR + script_path, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        if content_length > 0:
            p.stdin.write(bytes(content, 'utf-8)'))
            p.stdin.close()

        data = await p.stdout.read()
        print(data.decode('utf-8'))
    else:
        p = await asyncio.create_subprocess_shell('cat ' + DIR + script_path, stdout=asyncio.subprocess.PIPE)
        data = await p.stdout.read()

        print(data.decode('utf-8'))

    return web.Response(headers=headers, text=data.decode('utf-8'))


def main():
    global PORT
    global DIR
    PORT = int(sys.argv[1])
    DIR = sys.argv[2]

    my_server = web.Application()
    my_server.router.add_route('GET', '/{tail:.*}', handler)
    my_server.router.add_route('POST', '/{tail:.*}', handler)
    web.run_app(my_server, host='localhost', port=PORT)


if __name__ == '__main__':
    main()
