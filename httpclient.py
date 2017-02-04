#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Modifications Copyright 2017 Kalvin Eng
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        return s

    def get_code(self, data):
        return int(data[0].split()[1])

    def get_headers(self,data):
        return ''.join(data[:-1])

    def get_body(self, data):
        return data[-1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        # get host and port
        urlParsed = urlparse.urlsplit(url)
        host = urlParsed.hostname
        port = 80 if urlParsed.port is None else urlParsed.port
        s = self.connect(host, port)

        # build and send message
        message = "GET /" + urlParsed.path + " HTTP/1.1\r\n"
        if port and port!=80:
            message+="Host: {}:{}\r\n\r\n".format(host, port)
        else:
            message+="Host: {}\r\n\r\n".format(host)
        s.send(message)

        # parse response
        data = self.recvall(s).split("\r\n")
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # get host and port
        urlParsed = urlparse.urlsplit(url)
        host = urlParsed.hostname
        port = 80 if urlParsed.port is None else urlParsed.port
        body = urllib.urlencode(args) if args else ""
        s = self.connect(host, port)

        # build and send message with body
        message = "POST /" + urlParsed.path + " HTTP/1.1\r\n"
        if port and port!=80:
            message+="Host: {}:{}\r\n".format(host, port)
        else:
            message+="Host: {}\r\n".format(host)
        message += "Content-Type: application/x-www-form-urlencoded\r\n"
        message += "Content-Length: {}\r\n\r\n".format(len(body)) + body if body \
                     else "Content-length: 0\r\n\r\n"
        s.send(message)

        # parse response
        data = self.recvall(s).split("\r\n")
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
