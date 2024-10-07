from server import Server
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serv = Server(socket.gethostname(), 8080, 20)
serv = Server('127.0.0.1', 8080, 23)
serv.start_server()
