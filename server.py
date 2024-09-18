import socket

def start_server():
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('::', 12345))  # Bind to port 12345
    server.listen(1)  # Listen for 1 connection
    print("Server is listening on port 12345...")

    conn, addr = server.accept()
    print(f"Connected by {addr}")

    while True:
        # Receive message from client
        message = conn.recv(1024).decode('utf-8')
        if not message:
            print("Connection closed by client.")
            break
        print(f"Client: {message}")

        # Send reply to client
        reply = input("You: ")
        conn.send(reply.encode('utf-8'))

    conn.close()

if __name__ == "__main__":
    start_server()
