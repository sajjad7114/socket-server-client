import socket
from base64 import b64decode, b64encode

ENCODING = 'utf-8'


def serialize(path):
    with open(path, 'rb') as open_file:
        byte_content = open_file.read()
    base64bytes = b64encode(byte_content)
    base64_string = base64bytes.decode(ENCODING)
    return base64_string


def generate_request():
    total_request = ''
    Input = input('Say Something:\n')
    if Input == 'end':
        return {'request': ''}
    request_method = Input.split(' ')[0]
    file_name = Input.split(' ')[1].split('/')[-1]
    check = True
    while Input != 'end':
        if check:
            total_request += Input + '\n'
        check = True
        Input = input()
        if Input.split(' ')[0] == 'serial':
            path = ''.join(i + ' ' for i in Input.split(' ')[1:])[:-1]
            try:
                Input = serialize(path)
            except:
                print("ERROR: file did not found!")
                check = False
        if Input.split(' ')[0] == 'read':
            path = ''.join(i + ' ' for i in Input.split(' ')[1:])[:-1]
            try:
                with open(path, 'r') as open_file:
                    Input = open_file.read()
            except:
                print("ERROR: file did not found!")
                check = False

    return {'request': total_request[:-1],
            'method': request_method,
            'file': file_name}


if __name__ == "__main__":
    ClientSocket = socket.socket()
    host = '127.0.0.1'
    port = 1233

    print('Waiting for connection')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))

    Response = ClientSocket.recv(1024)
    while True:
        request_dict = generate_request()
        request = request_dict['request']
        if not request:
            break
        print()
        method = request_dict['method']
        finish = True
        while finish:
            if len(request) >= 2048:
                req = request[:2048]
                request = request[2048:]
            else:
                req = request
                finish = False

            ClientSocket.send(str.encode(req))

        response = b''
        received = ClientSocket.recv(1024)
        response += received
        while len(received) == 1024:
            received = ClientSocket.recv(1024)
            response += received
        res = response.decode(ENCODING)

        splited = res.split('\n\n')
        header = splited[0]

        lines = header.split('\n')
        status = lines[0]
        status_num = int(status.split(' ')[1])

        headers = {}
        for line in lines[1:]:
            arr = line.split(': ')
            headers[arr[0]] = arr[1]

        content_length = int(headers['Content-Length'])
        content_type = headers['Content-Type']
        file_type = content_type.split('/')[0]

        body = res[-content_length:]

        if status_num != 200 or method == 'POST':
            print(res)

        else:
            print(header)
            file = request_dict['file']
            path = content_type + '/' + file
            if file_type == "image":
                print("image received")
                base64_bytes = body.encode(ENCODING)
                b64encode = b64decode(base64_bytes)
                with open(path, 'wb+') as f:
                    f.write(b64encode)
                f.close()
            else:
                print("text received")
                with open(path, 'w+') as f:
                    f.write(body)
                f.close()

        connection = headers['Connection']
        if connection == 'close':
            break

    ClientSocket.close()
