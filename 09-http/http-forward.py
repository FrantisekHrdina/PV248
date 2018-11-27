#!/usr/bin/env python3

import http
import sys
import urllib
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from io import StringIO
from urllib import request


def is_json(tested_string):
    try:
        json_object = json.loads(tested_string)
    except ValueError:
        return False
    return True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generating headers
        headers = self.headers._headers
        dict_headers = {}
        for item in headers:
            if item[0] == 'Host':
                dict_headers[item[0].encode('ascii')] = (TARGET).encode('ascii')
            else:
                dict_headers[item[0].encode('ascii')] = item[1].encode('ascii')

        # Client part
        # # First option
        # # START
        # conn = http.client.HTTPConnection(TARGET)
        # conn.request("GET", "", dict_headers)
        # resp = conn.getresponse()
        # data = resp.read()
        # # END

        fwd_headers = dict(self.headers)
        if 'Host' in fwd_headers:
            #fwd_headers['Host'] = TARGET
            del fwd_headers['Host']

        req = urllib.request.Request(url='http://' + TARGET, data=None, method='GET', headers=fwd_headers)


        response = {}

        try:
            with urllib.request.urlopen(req, timeout=1) as r:
                response['code'] = r.status
                response['headers'] = dict(r.headers._headers)
                response_content = r.read()
                print(response_content)

                if is_json(response_content):
                    response['json'] = json.loads(response_content.decode('utf-8'))

                else:
                    response['content'] = response_content.decode('UTF-8')

                # self.send_header('Content-Type', 'application/json')



                pass
        except Exception as ex:
            print(ex)
            response['code'] = 'timeout'

        finally:
            json_response = str(json.dumps(response))
            json_response = bytes(json_response, 'utf-8')
            # self.send_header('Content-Type', 'application/json')
            self.wfile.write(json_response)
            self.do_HEAD()

        # self.wfile.write(json.dumps(response))





        print(response)
        # response['json'] = r.rfile.read(int(self.headers.get('Content-Length')))



        self.do_HEAD()
        sys.exit()

        return

    def do_POST(self):
        response = {}
        response['code'] = None
        try:
            input_json = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        except Exception:
            response['code'] = 'invalid json'

        print(input_json)


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

        print(headers)


        try:
            url = input_json['url']
            if type == 'POST':
                content = input_json['content']
        except Exception:
            response['code'] = 'invalid json'



        if response['code'] != 'invalid json':
            req = urllib.request.Request(url=url, method=type)

            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    response['code'] = r.status
                    response['headers'] = dict(r.headers._headers)
                    response_content = r.read()

                    if is_json(response_content):
                        response['json'] = json.loads(response_content.decode('utf-8'))
                        #response['json'] = response_content.decode('utf-8')

                    else:
                        response['content'] = response_content.decode('utf-8')

                    # self.send_header('Content-Type', 'application/json')

                    pass
            except Exception:
                response['code'] = 'timeout'

            finally:
                json_response = str(json.dumps(response))
                json_response = bytes(json_response, 'utf-8')
                self.wfile.write(json_response)




        self.do_HEAD()
        print('POST')




        sys.exit()
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
