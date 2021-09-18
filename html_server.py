import socket

ENCODING = 'utf-8'
s = socket.socket()
port = 9000
s.bind(('127.0.0.1', port))

print('Starting server on localhost', port)
print('The Web server URL for this would be http://localhost:%d/' % port)

s.listen(5)

print('Entering infinite loop; hit CTRL-C to exit')
while True:
    c, (client_host, client_port) = s.accept()
    print('Got connection from', client_host, client_port)
    print(c.recv(1024))
    c.send('HTTP/1.0 200 OK\n'.encode(ENCODING))
    c.send('Content-Type: text/html; charset=utf-8\n\n'.encode(ENCODING))
    c.send("""
        <html>
            <body style="text-align:center;">
                <h1>Hello from Sajjad Salari</h1>
                <h2>Final Project of Data Network</h2>
            </body>
        </html>
        """.encode(ENCODING))
    c.close()

# b'GET / HTTP/1.1\r\nHost: localhost:9000\r\nConnection: keep-alive\r\nsec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"\r\nsec-ch-ua-mobile: ?0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9,fa;q=0.8\r\nCookie: _ga=GA1.1.712086962.1624530981\r\n\r\n'
# Got connection from 127.0.0.1 50280