#!/usr/bin/env python
"""toy server for playing with networking in python"""

#David Lichtenberg
#dmlicht
#david.m.lichtenberg@gmail.com


import socket
import server_constants

def construct_header(http_ver, status_code):
    """returns appropriate response header"""
    return http_ver + ' ' + str(status_code) + ' ' + server_constants.REASON_PHRASES[status_code]

class HTTPMessage(object):
    def __init__(self, msg):
        tokens = msg.split()
        self.method = tokens[0]
        self.resource = tokens[1]
        self.version = tokens[2]

        #TODO: fix parameter parsing, not working properly
        self.params = {}
        for i in xrange(3, len(tokens), 2):
            self.params[tokens[i]] = tokens[i+1]

class HTTPServer(object):
    def __init__(self, handlers):
        self.handlers = handlers
        self.run()

    def handle_msg(self, msg):
        """returns header and body (if applicable) for given request"""
        http_msg = HTTPMessage(msg)
        response_body = ""
        if http_msg.method in self.handlers:
            status_code, response_body = self.handlers[http_msg.method](http_msg.resource)
        elif http_msg.method in server_constants.METHODS:
            status_code = 501 #Is okay request but not implemented
        else:
            status_code = 400 #Not a supported method
        response_header = construct_header(http_msg.version, status_code)
        return response_header, response_body

    def run(self):
        host = '' #accept requests from all interfaces
        
        port = 9000 #use port 80 as binding port

        #Initialize IPv4 (AF_INET) socket using TCP (SOCK_STREAM)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #set port to be reusable - this allows port to be freed when socket is closed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        clients_served = 0

        try:
            sock.bind((host, port))
        except socket.error, msg:
            print 'bind error, code: ', msg
            exit(0)

        #begin listening allowing for one connection at a time

        try:
            sock.listen(1)
        except socket.error:
            exit(0)

        while 1:
            client_socket, client_addr = sock.accept()
            msg = client_socket.recv(2048)

            #TODO: spin off new thread
            outgoing_header, outgoing_body = self.handle_msg(msg)

            try:
                client_socket.send(msg)
                client_socket.send(outgoing_body)
            except socket.error, e:
                print "error sending out file: ", e
            clients_served += 1
            print 'clients served:', clients_served
            client_socket.close()

