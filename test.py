#!usr/bin/env Python

from email.utils import formatdate
import http_server
from os import listdir, fork, _exit
import socket
import unittest


class test_receive(unittest.TestCase):  # Attribution: Matt D. in collaboration
                                        # with Luke P. and James W.
    """ Tests receive() method in http_server.py """
    def setUp(self):
        self.empty_message = ''
        self.short_message = 'Darling'
        self.long_message = '3.1415926535897932384626433832795028841971693993'
        self.exact_message = 'abcdefghijklmnopqrstuvwxyz123456'

    def test_empty(self):
        pid = fork()
        if pid:
            server = self.temp_server()
            conn, addr = server.accept()
        else:
            self.temp_client(self.empty_message)
            _exit(0)
        self.assertEqual(http_server.receive(conn, 32), self.empty_message)

    def test_short(self):
        pid = fork()
        if pid:
            server = self.temp_server()
            conn, addr = server.accept()
        else:
            self.temp_client(self.short_message)
            _exit(0)
        self.assertEqual(http_server.receive(conn, 32), self.short_message)

    def test_long(self):
        pid = fork()
        if pid:
            server = self.temp_server()
            conn, addr = server.accept()
        else:
            self.temp_client(self.long_message)
            _exit(0)
        self.assertEqual(http_server.receive(conn, 32), self.long_message)

    def test_exact(self):
        pid = fork()
        if pid:
            server = self.temp_server()
            conn, addr = server.accept()
        else:
            self.temp_client(self.exact_message)
            _exit(0)
        self.assertEqual(http_server.receive(conn, 32), self.exact_message)

    def temp_server(self):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        sock.bind(('127.0.0.1', 50000))
        sock.listen(1)
        return sock

    def temp_client(self, msg):
        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_IP)
        client_socket.connect(('127.0.0.1', 50000))
        client_socket.sendall(msg)
        client_socket.shutdown(socket.SHUT_WR)
        client_socket.close()


class test_parse(unittest.TestCase):
    """ Tests parse() method in http_server.py """
    def setUp(self):
        self.recv = """GET /path/to/index.html HTTP/1.1\r\nabcdefghijklmnopqrstuvwxyz"""
        self.method = "GET"
        self.URI = "/path/to/index.html"
        self.protocol = "HTTP/1.1"
        self.body = "abcdefghijklmnopqrstuvwxyz"

    def test_parse_method(self):
        self.assertEqual(self.method, http_server.parse(self.recv)[0])

    def test_parse_URI(self):
        print self.URI
        print http_server.parse(self.recv)[1]
        self.assertEqual(self.URI, http_server.parse(self.recv)[1])

    def test_parse_protocol(self):
        self.assertEqual(self.protocol, http_server.parse(self.recv)[2])

    def test_parse_body(self):
        self.assertEqual(self.body, http_server.parse(self.recv)[3])


class test_mapURI(unittest.TestCase):
    """ Tests map_URI() method in http_server.py """
    def setUp(self):
        self.directory_request = '/images'
        self.image_request = '/images/sample_1.png'
        self.text_request = '/sample.txt'
        self.bad_request = '/fuubar'

    def test_directory_request(self):
        content_type, message = http_server.map_URI(self.directory_request)
        contents = listdir('webroot' + self.directory_request)
        expected = '\r\n'.join(contents)
        self.assertEqual(message, expected)
        self.assertEqual(content_type, 'text/plain')

    def test_image_request(self):
        content_type, message = http_server.map_URI(self.image_request)
        with open('webroot' + self.image_request, 'rb') as infile:
            expected = infile.read()
        self.assertEqual(message, expected)
        self.assertEqual(content_type, 'image/png')

    def test_text_request(self):
        content_type, message = http_server.map_URI(self.text_request)
        with open('webroot' + self.text_request, 'rb') as infile:
            expected = infile.read()
        self.assertEqual(message, expected)
        self.assertEqual(content_type, 'text/plain')

    def test_best_request(self):
        self.assertRaises(http_server.Error404, http_server.map_URI,
                          self.bad_request)


class test_respond(unittest.TestCase):  # MARK C. IS BRILLIANT
    """ Tests respond() method in http_server.py """
    def setUp(self):
        self.file_type = "text/html"
        self.file_body = "<!DOCTYPE html>\n<html>\n<body>\n\n<h1>North Carolina</h1>\n\n<p>A fine place to spend a week learning web programming!</p>\n\n</body>\n</html>\n\n"
        self.file_response = "HTTP/1.1 200 OK\r\nDate: " + formatdate(usegmt=True) + "\r\nContent-Type: text/html; Character-Type: UTF-8\r\nContent-Length: 136\r\n\r\n<!DOCTYPE html>\n<html>\n<body>\n\n<h1>North Carolina</h1>\n\n<p>A fine place to spend a week learning web programming!</p>\n\n</body>\n</html>\n\n"

        self.dir_type = "text/plain"
        self.dir_body = "/images\r\n\tJPEG_example.jpg\r\n\tSample_Scene_Balls.jpg\r\n\tsample_1.png"
        self.dir_response = "HTTP/1.1 200 OK\r\nDate: " + formatdate(usegmt=True) + "\r\nContent-Type: text/plain; Character-Type: UTF-8\r\nContent-Length: 66\r\n\r\n/images\r\n\tJPEG_example.jpg\r\n\tSample_Scene_Balls.jpg\r\n\tsample_1.png"

    def test_respond(self):
        self.assertEqual(http_server.respond(self.file_type, self.file_body),
                         self.file_response)
        self.assertEqual(http_server.respond(self.dir_type, self.dir_body),
                         self.dir_response)

if __name__ == '__main__':
    unittest.main()
