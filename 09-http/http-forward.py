#!/usr/bin/env python3

import sys
import urllib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib import request


def is_json(tested_string):
    try:
        json_object = json.loads(tested_string)
    except Exception:
        return False
    return True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generating headers
        fwd_headers = dict(self.headers)
        if 'Host' in fwd_headers:
            del fwd_headers['Host']

        fwd_headers['Accept-Encoding'] = 'identity'


        path_and_params = self.requestline.split(' ')[1]
        req = urllib.request.Request(url='http://' + TARGET + path_and_params, data=None, method='GET', headers=fwd_headers)

        response = {}
        try:
            with urllib.request.urlopen(req, timeout=1) as r:
                response['code'] = r.status
                response['headers'] = dict(r.headers._headers)
                response_content = r.read()

                if is_json(response_content):
                    response['json'] = json.loads(response_content.decode('utf-8'))

                else:
                    response['content'] = response_content.decode('utf-8')
        except Exception as ex:
            response['code'] = 'timeout'

        finally:
            json_response = str(json.dumps(response, ensure_ascii=False, indent=4))
            json_response = bytes(json_response, 'utf-8')
            self.do_HEAD()
            self.wfile.write(json_response)

        return

    def do_POST(self):
        response = {}
        response['code'] = None
        try:
            input_json = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        except Exception:
            response['code'] = 'invalid json'

        type = 'GET'
        url = None
        headers = {}
        content = None
        timeout = 1


        try:
            type = input_json['type']
        except Exception:
            pass

        try:
            headers = input_json['headers']
        except Exception:
            pass

        try:
            timeout = input_json['timeout']
        except Exception:
            pass

        try:
            url = input_json['url']
            if type == 'POST':
                content = input_json['content']
        except Exception:
            response['code'] = 'invalid json'

        if response['code'] != 'invalid json':
            headers['Accept-Encoding'] = 'identity'

            if content is None:
                data = None
            else:
                data = bytes(content, 'utf-8')

            req = urllib.request.Request(url=url, method=type, headers=headers, data=data)

            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    response['code'] = r.status
                    response['headers'] = dict(r.headers._headers)

                    response_content = r.read()

                    if is_json(response_content):
                        response['json'] = json.loads(response_content.decode('utf-8'))
                    else:
                        response['content'] = response_content.decode('utf-8')
            except Exception as ex:
                # print(ex)
                response['code'] = 'timeout'

        json_response = str(json.dumps(response, ensure_ascii=False, indent=4))
        json_response = bytes(json_response, 'utf-8')
        self.do_HEAD()
        self.wfile.write(json_response)


        return

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        return


PORT = int(sys.argv[1])
TARGET = sys.argv[2]
server = HTTPServer(('', PORT), Handler)
server.serve_forever()
