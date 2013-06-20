#!/usr/bin/env python

import HTTPserver

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


def get_get(route):
    """handles get request - returns appropriate data and response code"""
    response_status_code = 200
    response_body = ""
    resource_path = parse_route(route)
    try:
        f = open(resource_path)
        response_body = f.read()
    except Exception as e:
        print e
        response_status_code = 404
    return response_status_code, response_body


def get_head(route):
    """returns response code"""
    response_status_code = 200
    resource_path = parse_route(route)
    response_body = ""
    try:
        open(resource_path)
    except IOError:
        response_status_code = 404
    except Exception as e:
        print e
        raise Exception
    return response_status_code, response_body


def get_options():
    pass


if __name__ == '__main__':
    main()

