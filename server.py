import os
from socket import *
import threading


class Server:
    def __init__(self, addr, port, timeout):
        self.addr = addr
        self.port = port
        self.timeout = timeout
        self.serverSocket = None
        self.sessions = dict()
        self.clientAddr = None

    def server_socket(self):
        try:
            self.serverSocket = socket(AF_INET, SOCK_STREAM)
            self.serverSocket.bind((self.addr, self.port))
            self.serverSocket.listen(5)
            serverIp, serverPort = self.serverSocket.getsockname()
            print(f"Server Started at: {serverIp}, Port, {serverPort}")
            print("listening")
            self.serverSocket.settimeout(self.timeout)
            while True:
                try:
                    client_socket, client_addr = self.serverSocket.accept()
                    self.clientAddr = client_addr[0]
                    print(f"Accepted connection from {client_addr}")
                    thread = threading.Thread(target=self.handle_request, args=(client_socket,))
                    thread.start()
                except TimeoutError as e:
                    print(e)
                    self.stop_server()
                    break
        except Exception as e:
            print(e)
            self.stop_server()

    def start_server(self):
        try:
            self.server_socket()
        except TimeoutError:
            self.stop_server()

    def stop_server(self):
        if self.serverSocket:
            print("Shutting Down Server...")
            self.serverSocket.shutdown(SHUT_RDWR)
            self.serverSocket = None

    def parse_request(self, request_data):
        lines = request_data.split('\r\n')
        request = lines[0]
        header = {}
        body = ''
        for i in range(1, len(lines)):
            line = lines[i]
            if line == '':
                body = '\r\n'.join(lines[i + 1:])
                break
            if ': ' in line:
                headKey, headValue = line.split(': ', 1)
                header[headKey] = headValue

        return request, header, body

    def handle_request(self, client_socket):
        try:
            requestedData = client_socket.recv(4096).decode()
            request, header, body = self.parse_request(requestedData)
            splitRequest = request.split(" ")
            if len(splitRequest) == 3:
                method, path, version = splitRequest
                if path == "/":
                    path = "assets/index.html"
                if method == "GET":
                    self.handle_get_request(client_socket, path)
                elif method == "POST":
                    self.handle_post_request(client_socket, path, header, body)
                else:
                    self.handle_unsupported_method(client_socket, method)
            else:
                msg = "Request Invalid, Number of Elements not 3"
                client_socket.sendall(msg.encode())
        except Exception as e:
            print(e)

    def handle_unsupported_method(self, client_socket, method):
        header = "HTTP/1.1 405 Method Not Allowed\r\n"
        body = "<html><body><p>" + method + " method is not supported" + "</p></body></html>"
        header += f"Content-Length: {len(body)}\r\n"
        header += "Content-Type: text/html\r\n\r\n"
        client_socket.sendall(header.encode("utf-8") + body.encode("utf-8"))

    def handle_404(self, client_socket):
        header = "HTTP/1.1 404 Not Found\r\n"
        body = "<html><body><h1>404 Not Found</h1></body></html>"
        header += f"Content-Length: {len(body)}\r\n"
        header += "Content-Type: text/html\r\n\r\n"
        client_socket.sendall(header.encode("utf-8") + body.encode("utf-8"))

    def handle_get_request(self, client_socket, file_path):
        try:
            if os.path.exists(file_path):
                header = "HTTP/1.1 200 OK\r\n"
                with open(file_path, 'r') as file:
                    body = file.read()
                if self.clientAddr in self.sessions:
                    body = body.replace("{{name}}", self.sessions.get(self.clientAddr))
                header += f"Content-Length: {len(body)}\r\n"
                header += "Content-Type: text/html\r\n\r\n"
                client_socket.sendall(header.encode('utf-8') + body.encode('utf-8'))
            else:
                self.handle_404(client_socket)
        except Exception as e:
            print(f"Exception: {e}")

    def handle_post_request(self, client_socket, path, headers, body):
        name = body.split("=")[1]
        if path == "/change_name":
            self.sessions[self.clientAddr] = name
            header = "HTTP/1.1 200 OK\r\n"
            body = "<html><body><h1>Name Updated</h1></body></html>"
            header += f"Content-Length: {len(body)}\r\n"
            header += "Content-Type: text/html\r\n\r\n"
            client_socket.sendall(header.encode('utf-8') + body.encode('utf-8'))
        else:
            self.handle_404(client_socket)
