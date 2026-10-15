import os
import socket
import multiprocessing

SOCKET_PATH = "/tmp/calc_socket"

def handle_client(conn):
    try:
        data = conn.recv(1024).decode().strip()
        if data:
            print(f"Unix Socket сервер получил: {data}")
            try:
                res = str(eval(data))
            except Exception as e:
                res = f"Error: {e}"
            conn.sendall(res.encode())
    finally:
        conn.close()

if __name__ == "__main__":
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    print("Unix Socket Server запущен...")
    try:
        while True:
            conn, _ = server.accept()
            p = multiprocessing.Process(target=handle_client, args=(conn,))
            p.start()
            conn.close()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        print("Unix Socket Server остановлен и очищен.")
