import socket
import sys

SOCKET_PATH = "/tmp/calc_socket"
expr = sys.argv[1] if len(sys.argv) > 1 else "10*10"

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(SOCKET_PATH)
client.sendall(expr.encode())
response = client.recv(1024).decode()
print(f"Ответ от сокет-сервера: {response}")
client.close()
