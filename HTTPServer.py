#!/usr/bin/env python3
# See https://docs.python.org/3.2/library/socket.html
# for a decscription of python socket and its parameters
import socket

from threading import Thread
from argparse import ArgumentParser

BUFSIZE = 4096

def send_response_code(code, client_sock):
    client_sock.send(bytes('HTTP/1.1 {}\n'.format(code), 'utf-8'))

def send_header_fields(header, client_sock):
    client_sock.send(bytes('{}\n'.format(header), 'utf-8'))

# this function requires that the body is already in byte form
def send_body(body, client_sock):
    client_sock.send(body)

def send_header(response, fields, client_sock):
    send_response_code(response, client_sock)
    for field in fields:
        send_header_fields(field, client_sock)

def get_html(file, client_sock):
    print('Getting HTML\n')

    header = []
    body = None
    with open(file.removeprefix('/'), 'r') as fd:
        body = bytes(fd.read(),  'utf-8')
    header.append('Content-Type:text/html')
    header.append('Content-Length:{}'.format(len(body)))
    send_header(200, header, client_sock)

    client_sock.send(bytes('\n', 'utf-8'))
    send_body(body, client_sock)

    print('Done Getting HTML\n')

def get_image(file, type, client_sock):
    print('Getting Image\n')

    header = []
    body = None
    with open(file.removeprefix('/'), 'rb') as fd:
        if type == 'png':
            header.append('Content-Type:image/png')
        else:
            header.append('Content-Type:image/jpeg')
        body = fd.read()
    header.append('Content-Length:{}'.format(len(body)))

    send_header(200, header, client_sock)
    client_sock.send(bytes('\n', 'utf-8'))
    send_body(body, client_sock)

    print('Done Getting Image\n')

def get_mp3(file, client_sock):
    print('Getting MP3\n')

    header = []
    body = None
    with open(file.removeprefix('/'), 'rb') as fd:
        body = fd.read()
    header.append('Content-Type:audio/mpeg')
    header.append('Content-Length:{}'.format(len(body)))

    send_header(200, header, client_sock)
    client_sock.send(bytes('\n', 'utf-8'))
    send_body(body, client_sock)

    print('Done Getting MP3\n')

def get(file, client_sock, client_addr):
    print('GETTING', file)
    (name, sep, type) = file.partition('.')
    try:
        if type == 'png' or type == 'jpg':
            get_image(file, type, client_sock)
        elif type == 'html':
            get_html(file, client_sock)
        else:
            get_mp3(file, client_sock)
    except FileNotFoundError:
        client_sock.send(bytes('HTTP/1.1 404\n', 'utf-8'))
        client_sock.send(bytes('Content-Type:text/HTML\n\n', 'utf-8'))
        with open('404.html', 'r') as fd:
            client_sock.send(bytes(fd.read(), 'utf-8'))


def head(file, client_sock, client_addr):
    (name, sep, type) = file.partition('.')
    try:
        with open(file, 'rb') as fd:
            body = fd.read()
            header = []
            if type == 'jpg':
                header.append('Content-Type:image/jpeg')
            elif type == 'png':
                header.append('Content-Type:image/png')
            elif type == html:
                header.append('Content-Type:text/html')
            elif type == mp3:
                header.append('Content-Type:audio/mpeg')

            header.append('Content-Length:{}'.format(len(body)))
            send_header(200, header, client_sock)
    except FileNotFoundEror:
        send_response_code(404, client_sock)
    print('HEAD request')

def post(data, client_sock, client_addr):
    # finding form data in the request
    found = False
    body = ''
    for line in data.splitlines():
        if found == True:
            body = body + line
        if found == False and line == '':
            found = True

    dct = dict()
    for key_val in body.split('&'):
        split = key_val.split('=')
        dct[split[0]] = split[1]

    print(dct)

    html_form_response = '''<!DOCTYPE html>
    <html>
        <meta charset="utf-8">
        <meta title="response">
    <head>

    </head>
    <body>
        <table>
            <tr>
                <td>Event</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>Day</td>
                <td>{}</td>
            <tr>
            <tr>
                <td>Start</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>End</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>Phone</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>Location</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>Info</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>URL</td>
                <td>{}</td>
            </tr>
        </table>
    </body>
    </html>
    
    '''.format(dct['event'], dct['day'], dct['start'], dct['end'], dct['phone'], dct['location'], dct['info'], dct['url'])

    print(html_form_response)

    html_form_response = bytes(html_form_response, 'utf-8')

    header_fields = ['Content-Type:text/html', 'Context-Legnth:{}'.format(len(html_form_response))]
    send_header(200, header_fields, client_sock)
    send_body(html_form_response, client_sock)
    print('POST request')

def handle_http_request(data, client_sock, client_addr):
    (header, sep, tail) = data.partition('\n')
    methods = dict(GET=get, HEAD=head, POST=post)
    print(header)
    print(tail)
    try:
        (method, file, protocol) = header.split(' ')
        if method in methods:
            if method == 'GET' or method == 'HEAD':
                methods[method](file, client_sock, client_addr)
            else:
                methods[method](tail, client_sock, client_addr)
        else:
            client_sock.send(bytes('HTTP/1.1 405 Method not implemented\n'), 'utf-8')
    except ValueError:
        client_sock.send(bytes('HTTP/1.1 400 Bad Request\n', 'utf-8'))



def client_talk(client_sock, client_addr):
    print('talking to {}'.format(client_addr))
    data = client_sock.recv(BUFSIZE)
    while data:
      handle_http_request(data.decode('utf-8'), client_sock, client_addr)
      data = client_sock.recv(BUFSIZE)


    # clean up
    client_sock.shutdown(1)
    client_sock.close()
    print('connection closed.')

class HTTPServer:
  def __init__(self, host, port):
    print('listening on port {}'.format(port))
    self.host = host
    self.port = port

    self.setup_socket()

    self.accept()

    self.sock.shutdown()
    self.sock.close()

  def setup_socket(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((self.host, self.port))
    self.sock.listen(128)

  def accept(self):
    while True:
      (client, address) = self.sock.accept()
      th = Thread(target=client_talk, args=(client, address))
      th.start()

def parse_args():
  parser = ArgumentParser()
  parser.add_argument('--host', type=str, default='localhost',
                      help='specify a host to operate on (default: localhost)')
  parser.add_argument('-p', '--port', type=int, default=5050,
                      help='specify a port to operate on (default: 5050)')
  args = parser.parse_args()
  return (args.host, args.port)


if __name__ == '__main__':
  (host, port) = parse_args()
  HTTPServer(host, port)
