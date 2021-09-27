#  coding: utf-8 
import socketserver
from os import path


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        # parse the data received to method, url and HTTP_version
        self.data = self.request.recv(1024).strip().decode("utf-8")
        request_info = self.data.split('\n')[0]
        # print("Got a request of: " + request_info + '\n')

        try:
            method, url, HTTP_version = request_info.split(' ')
        except ValueError:
            # catch error if there is no three items after split
            return
        # print('current url is', url)

        # check if www is in url
        if 'www' not in url:
            origin_url = url  # save origin url to be returned later for redirecting
            url = 'www' + url
        if url[0] == '/':
            url = url[1:]

        if method != "GET":
            # if the method used is not get, report 405
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed!\r\n\r\n", 'utf-8'))
        else:
            # if the url provided is neither a file nor a directory, report 404
            if not path.exists(url) or not self.check_safety(url):
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found!\r\n\r\n", 'utf-8'))
            if path.isdir(url):  # if the url is a directory
                if url[-1] != '/':
                    # redirect
                    url += '/'
                    origin_url += '/'
                    self.request.sendall(
                        bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation:" + origin_url + "\r\n\r\n", 'utf-8'))
                else:
                    # go to index.html under that directory if no file is specified
                    url += 'index.html'

            if url[-5:] == '.html':
                file_type = 'html'
            elif url[-4:] == '.css':
                file_type = 'css'
            else:
                file_type = ''
            if path.isfile(url):
                f = open(url, 'r')
                self.request.sendall(bytearray(
                    "HTTP/1.1 200 OK Not FOUND!\r\n" + "Content-Type: text/" + file_type + '\r\n\r\n' + f.read() + '\r\n\r\n',
                    'utf-8'))
                f.close()

    def check_safety(self, url):
        # check if the .. is out of bound
        abs_path = path.dirname(path.realpath(__file__))
        previous_directories = abs_path.split('/')[1:]
        url_going_backward = url.split('/')
        if len(previous_directories) > url_going_backward.count('..'):
            return True
        return False


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
