import socket
from _thread import *
import datetime
from base64 import b64encode, b64decode
import json


ENCODING = 'utf-8'
statuses = {400: ['Bad Request', 'BADREQUEST!', ''],
            501: ['Not Implemented', 'NOTIMPLEMENTED!', ''],
            405: ['Method Not Allowed', 'NOTALLOWED!', '\nAllow: GET'],
            301: ['Moved Permanently', 'MOVEDPERMANENTLY!', ''],
            403: ['Forbidden', 'FORBIDDEN!', ''],
            200: ['Ok', 'POST!', '']}
methods = ['GET', 'POST', 'DELETE', 'HEAD', 'PUT']
FORBIDDEN = '<html><body><h1>THISISFORBIDDEN!</h1></body></html>'
CONNECTION = ['HTTP/1.0', 'HTTP/1.1']
CONNECTION_MESSAGE = ['close', 'open']


def now():
    return datetime.datetime.now().strftime("%a, %d %b %y %H:%M:%S GMT")


def log(address, start=None, request=None):
    with open('log.json', 'r+') as jf:
        data = json.load(jf)
    jf.close()
    if start:
        data[address] = {"start": start, "requests": []}
    if request:
        data[address]["requests"].append(request)
    with open('log.json', 'w+') as jf:
        json.dump(data, jf, indent=4)
    jf.close()


def generate_reply(status, cc, content_type='text/html', body=''):
    stats["response"][status] += 1
    if not body:
        body = '<text><body><h1>{}</h1></body></text>'.format(statuses[status][1])

    reply = """{} {} {}\nConnection: {}\nContent-Length: {}\nContent-Type: {}{}\nDate: {}\n\n{}"""\
        .format(CONNECTION[cc-1], status, statuses[status][0], CONNECTION_MESSAGE[cc-1], len(body), content_type,
                statuses[status][2], now(), body)

    return reply, status


def check_format(head):
    lines = head.split('\n')
    first = lines[0]
    if len(first.split(' ')) != 3:
        return False

    for line in lines[1:]:
        if len(line.split(': ')) != 2:
            return False

    connection = first.split(' ')[2]
    if connection not in CONNECTION:
        return False
    return CONNECTION.index(connection) + 1


def check_method(head):
    method = head.split('\n')[0].split(' ')[0]
    if method not in methods:
        stats["request"]["Improper"] += 1
        return False
    stats["request"][method] += 1
    return method


def check_allowed_method(head):
    method = head.split('\n')[0].split(' ')[0]
    if methods.index(method) > 2:
        return False
    return True


def serialize(path):
    with open(path, 'rb') as open_file:
        byte_content = open_file.read()
    base64_bytes = b64encode(byte_content)
    base64_string = base64_bytes.decode(ENCODING)
    return base64_string


def handle_get(path, cc):
    try:
        file_type = path.split('/')[1]
        ext = path.split('/')[2]
        if file_type == "image":
            result = serialize(path)
        else:
            with open(path, 'r') as open_file:
                result = open_file.read()
        content_type = file_type+'/'+ext
        stats["file"][content_type] += 1
        return generate_reply(200, cc, content_type, result)
    except:
        return generate_reply(301, cc)


def handle_post(path, body, cc):
    if body == FORBIDDEN:
        return generate_reply(403, cc)
    try:
        file_type = path.split('/')[1]
        if file_type == "image":
            base64_bytes = body.encode(ENCODING)
            b64_encode = b64decode(base64_bytes)
            with open(path, 'wb+') as f:
                f.write(b64_encode)
            f.close()
        else:
            with open(path, 'w+') as f:
                f.write(body)
            f.close()
        return generate_reply(200, cc)
    except:
        return generate_reply(400, cc)


def handle_request(req, cc):
    head = req[0]
    first_line = head.split('\n')[0].split(' ')
    method = first_line[0]
    route = '.'+first_line[1]

    if method == 'POST':
        body = ''.join(i+'\n\n' for i in req[1:])[:-2]
        return handle_post(route, body, cc)
    else:
        return handle_get(route, cc)


def check_command(data):
    if data == "num of clients\r\n":
        return "number of clients: " + str(ThreadCount - 1) + '\n', 2
    elif data == "file type stats\r\n":
        return ''.join(key + ': ' + str(stats["file"][key]) + '\n' for key in stats["file"]), 2
    elif data == "request stats\r\n":
        return ''.join(key + ': ' + str(stats["request"][key]) + '\n' for key in stats["request"]), 2
    elif data == "response stats\r\n":
        return ''.join(str(key) + ': ' + str(stats["response"][key]) + '\n' for key in stats["response"]), 2
    elif data == "disconnect\r\n":
        return 'bye\n', 1
    else:
        return False, 1


def threaded_client(connection, address):
    connection.send(str.encode('Welcome to the Server\n'))
    log(address[0]+':'+str(address[1]), start=now())
    while True:
        request = b''
        received = connection.recv(2048)
        request += received
        while len(received) == 2048:
            received = connection.recv(2048)
            request += received

        data = request.decode(ENCODING)
        if not data:
            break

        reply, connection_continue = check_command(data)
        if not reply:

            req = data.split('\n\n')
            head = req[0]

            method = check_method(head)

            connection_continue = check_format(head)
            if not connection_continue:
                reply, status = generate_reply(400, 1)
            elif not method:
                reply, status = generate_reply(501, connection_continue)
                method = head.split(' ')[0]
            elif not check_allowed_method(head):
                reply, status = generate_reply(405, connection_continue)
            else:
                reply, status = handle_request(req, connection_continue)

            log(address[0]+':'+str(address[1]), request={"method": method,
                                                         "status": str(status)+' '+statuses[status][0],
                                                         "time": now()})

        finish = True
        while finish:
            if len(reply) >= 1024:
                res = reply[:1024]
                reply = reply[1024:]
            else:
                res = reply
                finish = False

            connection.send(str.encode(res))

        if connection_continue == 1:
            break

    connection.close()
    global ThreadCount
    print('Close Connection from: ' + address[0] + ':' + str(address[1]))
    ThreadCount -= 1
    print('Thread Number: ' + str(ThreadCount))


ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
stats = {
    "file": {"image/jpg": 0, "image/png": 0, "text/txt": 0, "text/html": 0},
    "request": {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0, "Improper": 0},
    "response": {200: 0, 301: 0, 400: 0, 403: 0, 405: 0, 501: 0}
}
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, address, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

