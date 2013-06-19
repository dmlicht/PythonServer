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
        #TODO: implement error checking
        #NOTE: will cause error is no double newline following head
        header = msg.split('\n\n')[0] 
        header_lines = header.split('\r\n')
        request_line = header_lines[0]
        self.header_fields = self.parse_header_fields(header_lines[1:])
        self.method, self.resource, self.version = request_line.split()

    def parse_header_fields(self, header_field_lines):
        """takes newline seperated header and returns dict representation"""
        header_fields = {}
        for line in (line for line in header_field_lines if line.strip()):
            key, val = line.split(':', 1)
            header_fields[key] = val
        return header_fields

class Response(object):
    def __init__(self):
        pass
    def __repr__(self):
        pass
    def __str__(self):
        pass

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

