#!/usr/bin/env python
"""toy server for playing with networking in python"""

#David Lichtenberg
#dmlicht
#david.m.lichtenberg@gmail.com

import socket
import server_constants

class Request(object):
    def __init__(self, msg):
        #TODO: implement error checking
        #NOTE: will cause error is no double newline following head
        self.msg = msg
        request_chunks = msg.split('\r\n\r\n', 1)
        header = request_chunks[0]
        if len(request_chunks) == 2:
            self.body = request_chunks[1]
        else:
            self.body = None
        header_lines = header.split('\r\n')
        request_line = header_lines[0]
        self.header_fields = self.parse_header_fields(header_lines[1:])
        self.method, self.resource, self.version = request_line.split()

    def parse_header_fields(self, header_field_lines):
        """takes newline seperated header and returns dict representation"""
        header_fields = {}
        for key, val in (line.split(':', 1) for line in header_field_lines if line.strip()):
            header_fields[key] = val
        return header_fields

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "<Request: %s" % self

class Response(object):
    """Builds response message given response data and/or status code"""

    http_ver = 'HTTP/0.9'
    default_bodies = {
            200: "<html> ok </html>",
            400: "<html> unsupported method</html>",
            404: "<html> page not found </html>",
            501: "<html> method supported but not implemented</html>"
    }

    def __init__(self, status_code=200, body=None, **headers):
        self.status_code = status_code 
        self.body = body
        self.headers = headers
    
    @classmethod
    def convenience(cls, response):
        if response is None:
            return cls(404, None)
        if isinstance(response, int): #passed status code to function
            return cls(response, None)
        if not isinstance(response, cls): #we got something containing a body
            return cls(200, response)
        else:
            return response

    def _body_getter(self):
        return self._body

    def _body_setter(self, body):
        if body is None:
            self._body = self.default_bodies[self.status_code]
        else:
            self._body = body

    #property creates getters and setters on instance variables
    body = property(_body_getter, _body_setter)

    def _response_line(self):
        """returns a string of the response line"""
        return "{http_ver} {status_code} {reason_phrase}\r\n".format(
                http_ver = self.http_ver,
                status_code = self.status_code,
                reason_phrase = server_constants.REASON_PHRASES[self.status_code]
        )

    def _str_header_fields(self):
        """returns string representation of header fields"""
        return '\r\n'.join([k + ': ' + v for (k,v) in self.headers.items()]) + '\r\n\r\n'

    def __str__(self):
        return self._response_line() + self._str_header_fields() + self.body

    def __repr__(self):
        return "<Response: %s>" % self

class Server(object):
    def __init__(self, handlers):
        self.handlers = handlers
        self.run()

    def handle_msg(self, msg):
        """returns header and body (if applicable) for given request"""
        request = Request(msg)
        if request.method in self.handlers:
            response = self.handlers[request.method](request)
            response = Response.convenience(response)
        elif request.method in server_constants.METHODS:
            response = Response.convenience(501) #Is okay request but not implemented
        else:
            response = Response.convenience(400) #Not a supported method
        return response

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
            response = self.handle_msg(msg)

            try:
                #client_socket.send(msg)
                #print str(response)
                client_socket.send(str(response))
            except socket.error, e:
                print "error sending out file: ", e
            clients_served += 1
            print 'clients served:', clients_served
            client_socket.close()

