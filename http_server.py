#!usr/bin/env Python

from email.utils import formatdate
from mimetypes import guess_type
from os import listdir
from os.path import isfile, isdir
import socket


def http_server():
    """ HTTP server that listens for client requests """
    host, port, backlog, buffer_size = '127.0.0.1', 50000, 5, 4096
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
        socket.IPPROTO_IP)
    try:
        server_socket.bind((host, port))
        server_socket.listen(backlog)
        while True:
            try:
                conn, addr = server_socket.accept()
                request = receive(conn, buffer_size)
                method, URI, protocol, body = parse(request)
                if method != 'GET':
                    raise Error405
                else:
                    content_type, contents = map_URI(URI)
                    response = respond(content_type, contents)
            except Error404:
                response = respond('text/plain', 'File Not Found', '404')
            except Error405:
                response = respond('text/plain', 'Method Not Allowed', '405')
            except:
                response = respond('text/plain', 'Internal Server Error',
                                   '500')
            finally:
                conn.sendall(response)
                conn.close()
    finally:
        server_socket.close()


def receive(x, y):  # x = conn, y = buffer_size
    """ Compiles buffered strings into request """
    request = ''
    while True:
        buff = x.recv(y)
        request += buff
        if len(buff) < y:
            return request


def parse(x):  # x = request
    """ Chunks client request into method, URI, protocol, and body """
    message = x.split('\r\n', 1)
    line1, body = message[0].split(' ', 2), message[1]
    method, URI, protocol = line1[0], line1[1], line1[2]
    return method, URI, protocol, body


def map_URI(x):  # x = URI
    """ Maps URI to filesystem """
    path = 'webroot%s' % (x)
    if isfile(path):
        with open(path, 'rb') as infile:
            contents = infile.read()
        return (guess_type(path)[0], contents)
    if isdir(path):
        contents = listdir(path)
        return ('text/plain', '\r\n'.join(contents))
    raise Error404


def respond(x, y, code='200 OK'):  # x = content_type, y = contents
    """ Builds HTTP response to client """
    if not isinstance(y, bytes):
        y = y.encode('utf-8')
    header = []
    header.append('HTTP/1.1 %s' % code)
    header.append('Date: %s' % formatdate(usegmt=True))
    header.append('Content-Type: %s; Character-Type: UTF-8' % (x))
    header.append('Content-Length: %s' % str(len(y)))
    header.append('\r\n%s' % y)
    return '\r\n'.join(header)


class Error404(Exception):
    """ Exception raised when file not found """
    pass


class Error405(Exception):
    """ Exception raised when method not allowed """
    pass

if __name__ == '__main__':
    http_server()
