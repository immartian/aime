import socket
import threading
import time

status = 'available'  # Start with the status set to 'available'

# Function to handle status server (responding to status requests)
def start_status_server(status_port):
    status_server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # Using UDP for status check
    status_server.bind(('::', status_port))
    print(f"Status server is listening on port {status_port}...")

    while True:
        data, addr = status_server.recvfrom(1024)  # Receive status request
        print(f"Received status request from {addr}")
        if status == 'available':
            status_server.sendto(b'available', addr)
        else:
            status_server.sendto(b'busy', addr)

# Function to handle chat server (accepting incoming chat connections)
def start_chat_server(chat_port):
    global status
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('::', chat_port))
    server.listen(1)
    print(f"Chat server is listening on port {chat_port}...")

    conn, addr = server.accept()
    print(f"Connected by {addr} (as server)")
    status = 'busy'  # Mark node as busy once a chat starts

    while True:
        message = conn.recv(1024).decode('utf-8')
        if not message:
            print("Connection closed.")
            status = 'available'  # Mark as available after chat ends
            break
        print(f"Peer: {message}")
        reply = input("You: ")
        conn.send(reply.encode('utf-8'))

    conn.close()

# Function to check another peer's status before initiating a chat
def check_status(peer_ip, status_port):
    client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # Using UDP for status check
    try:
        client.sendto(b'status', (peer_ip, status_port))  # Send status request
        data, _ = client.recvfrom(1024)  # Receive status response
        return data.decode('utf-8')
    except socket.error as e:
        print(f"Error checking status: {e}")
        return 'unknown'
    finally:
        client.close()

# Function to initiate a chat as a client
def start_chat_client(peer_ip, chat_port):
    client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        client.connect((peer_ip, chat_port))
        print(f"Connected to {peer_ip}:{chat_port} (as client)")

        while True:
            message = input("You: ")
            client.send(message.encode('utf-8'))

            reply = client.recv(1024).decode('utf-8')
            if not reply:
                print("Connection closed by server.")
                break
            print(f"Server: {reply}")

    except socket.error as e:
        print(f"Failed to connect to the server: {e}")
    finally:
        client.close()

# Unified peer-to-peer node function
def p2p_node(peer_ip, status_port, chat_port):
    # Start the status server thread (for responding to status checks)
    threading.Thread(target=start_status_server, args=(status_port,), daemon=True).start()

    # Start the chat server thread (for accepting chat connections)
    threading.Thread(target=start_chat_server, args=(chat_port,), daemon=True).start()

    # Give time for servers to start up before checking status
    time.sleep(1)

    while True:
        # Check the status of the peer
        peer_status = check_status(peer_ip, status_port)
        if peer_status == 'available':
            print(f"Peer is available. Initiating chat...")
            start_chat_client(peer_ip, chat_port)  # Start chat as client
            break
        elif peer_status == 'busy':
            print(f"Peer is busy. Waiting...")
        else:
            print(f"Peer status unknown.")

        time.sleep(5)  # Check status again after a delay

if __name__ == "__main__":
    peer_ip = "201:e8c5:3538:87a3:aa54:7dfb:8008:fb2e"  # Replace with peer's Yggdrasil IP
    #peer_ip = "200:170:d1b:9552:79e7:2726:50aa:4f48"  # Replace with peer's Yggdrasil IP
    status_port = 12344  # Port for status checking
    chat_port = 12345  # Port for actual chat

    p2p_node(peer_ip, status_port, chat_port)

