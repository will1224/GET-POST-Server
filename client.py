import socket

HOST = '127.0.0.1'
PORT = 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST, PORT))
    print("Connected client")
    # sock.sendall(b"POST /change_name HTTP/1.1\r\nHost: localhost\r\nContent-Length: 9\r\n\r\nname=Alice")
    sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
    data = sock.recv(1028)
    print(data.decode('utf-8'))
except Exception as e:
    print("Cannot connect to the server:", e)
