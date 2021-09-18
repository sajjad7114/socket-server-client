# socket-server-client
There are 3 clients and a server. Every client can send something to the server or recieve from it. There is also a forbiden file that can't be sent.
To talk with the server you should write a complete request.
At the first there is 3 parts: the request method(only post and get are allowed), the url, the protocol.
After that you can have other information or a file. The file can be read by "read" command (for texts) and "serial" command (for image files).
There is some example you can use to help you.
# html server
The html_server.py is something different that is a simple server that can connect to your browser.
