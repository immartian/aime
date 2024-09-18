import socket

def start_client(server_ip):
    client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    try:
        client.connect((server_ip, 12345))  # Connect to server on port 12345
        print(f"Connected to server at {server_ip}:12345")

        while True:
            # Send message to server
            message = input("You: ")
            client.send(message.encode('utf-8'))

            # Receive reply from server
            reply = client.recv(1024).decode('utf-8')
            if not reply:
                print("Connection closed by server.")
                break
            print(f"Server: {reply}")

    except socket.error as e:
        print(f"Failed to connect to the server: {e}")

    finally:
        client.close()

if __name__ == "__main__":
    server_ip = "200:170:d1b:9552:79e7:2726:50aa:4f48"  # Replace with the Yggdrasil IP of Node A
    start_client(server_ip)
