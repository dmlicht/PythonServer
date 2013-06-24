#!/usr/bin/env python

import HTTPserver

#TODO: change methods to take request object

def main():
    handlers = {
        "GET": get_get,
        "HEAD": get_head,
        "OPTIONS": get_options
    }
    HTTPserver.Server(handlers)

def parse_route(route):
    """take in web route and returns appropriate route to resource"""
    if route == '/':
        route = '/index.html'
    while '../' in route:
        route = route.replace('../', '')
    return '.' + route


def get_get(request):
    """handles get request - returns appropriate data and response code
    eventually we'll have to add checking if file is okay"""
    resource_path = parse_route(request.resource)
    response_body = None
    try:
        f = open(resource_path)
        response_body = f.read()
        f.close()
    except IOError as e: #this corresponds to file not found
        print e
    except Exception as e:
        print e
        f.close()
    return response_body


def get_head(request):
    """returns response code"""
    response_status_code = 200
    resource_path = parse_route(request.resource)
    try:
        open(resource_path)
    except IOError:
        response_status_code = 404
    except Exception as e:
        print e
        raise Exception
    return response_status_code


def get_options():
    """STILL NEED IMPLEMENTATION"""
    pass


if __name__ == '__main__':
    main()

