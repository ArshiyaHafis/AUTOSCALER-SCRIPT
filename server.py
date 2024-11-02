import socket
import threading

def handle_client(client_socket):
    data = client_socket.recv(1024)
    print(f"Received {data.decode()}")
    response = str(sum(range(1, 1000000)))  
    client_socket.send(response.encode())
    client_socket.close()

def server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))  
    server.listen(5)
    print("Server started and waiting for connections...")

    while True:
        client, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    server()

