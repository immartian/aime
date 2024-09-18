import socket
import threading
import time

def listen_for_connections(port):
    """Function to listen for incoming connections."""
    listener = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
    listener.bind(('::', port))
    listener.listen(1)
    print(f"Listening for incoming connections on port {port}...")
    conn, addr = listener.accept()
    print(f"Connected by {addr}")
    return conn

def connect_to_peer(peer_ip, port):
    """Function to try connecting to a peer."""
    client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        client.connect((peer_ip, port))
        print(f"Connected to peer {peer_ip}:{port}")
        return client
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to {peer_ip}:{port}: {e}")
        return None

def handle_connection(sock, is_server):
    """Handles incoming and outgoing messages."""
    def receive_messages(sock):
        while True:
            try:
                message = sock.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"Peer: {message}")
            except socket.error as e:
                print(f"Error receiving message: {e}")
                break

    # Start a thread to listen for messages from the peer
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    # Send messages
    while True:
        try:
            message = input("You: ")
            sock.send(message.encode('utf-8'))
        except socket.error as e:
            print(f"Error sending message: {e}")
            break

def p2p_chat(peer_ip, local_port, remote_port):
    # Start listening on the local port (server mode)
    listener_thread = threading.Thread(target=listen_for_connections, args=(local_port,))
    listener_thread.start()

    # Try to connect to the peer on the remote port (client mode)
    sock = connect_to_peer(peer_ip, remote_port)
    if not sock:
        # If the connection fails, wait for the peer to connect to us
        listener_thread.join()
        sock = listen_for_connections(local_port)

    # Handle the connection (both sending and receiving messages)
    handle_connection(sock, is_server=False)

if __name__ == "__main__":
    peer_ip = "201:e8c5:3538:87a3:aa54:7dfb:8008:fb2e"  # Replace with peer's Yggdrasil IP
    #peer_ip = "200:170:d1b:9552:79e7:2726:50aa:4f48"  # Replace with peer's Yggdrasil IP
    local_port = 12345  # The port we will listen on
    remote_port = 12346  # The port our peer is listening on

    p2p_chat(peer_ip, local_port, remote_port)
