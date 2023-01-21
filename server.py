#  coding: utf-8 
import socketserver
import os
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


# for sending http response :https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only
# and https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

class MyWebServer(socketserver.BaseRequestHandler):
    
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        if self.data != "":
            if self.data.split()[0].decode() == "GET":
                self.handle_get(self.data)
            #if not a get request send 405
            else:
                self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\nAllow: GET\r\n\r\nContent-length:0")
            
        return
                
                    
    # handle the get request
    def handle_get(self, data):
        dir = os.path.join(os.getcwd(), "www")
        path = data.split()[1].decode()
        # append path to cwd
        if (path[0] != "/"):
            file = os.path.join(dir, path)
        else:
            file = os.path.join(dir, path[1:])
        file_correct = os.path.realpath(file)
        
        #check if file path is inside the www folder, this is just to handle cases where there are links in the request
        if os.path.commonprefix([dir, file_correct]) != dir:
            self.request.sendall(b"HTTP/1.1 404 Not Found\r\nContent-length:0")
            return
        
        if(file.endswith("/")):
            file_correct = file_correct + "/"
        #check if file is a directory
        if(os.path.isdir(file_correct) and file_correct.endswith("/")):
            file_correct = os.path.join(file_correct,"index.html")
        # if still a directory send 301
        if(os.path.isdir(file_correct)):
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\n Location: {file_correct}\r\nContent-length:0\r\nConnection: close",'utf-8'))
            return
        #if file doesnt exist send 404
        if(not os.path.exists(file_correct)):
            self.request.sendall(b"HTTP/1.1 404 Not Found\r\nContent-length:0")
            return
        #if file exists send content
        f = open(file_correct, "r")
        content = f.read()
        if (file_correct.endswith(".html")):
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-length:" + str(len(content)) + "\r\nContent-Type: text/html\r\n\r\n" + content,'utf-8'))
        else:
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-length:" + str(len(content)) + "\r\nContent-Type: text/css\r\n\r\n" + content,'utf-8'))
        
        
        
        
        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
