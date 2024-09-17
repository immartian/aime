import socket
import threading
import time

def listen_for_connections(port):
    """Function to listen for incoming connections."""
    listener = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    listener.bind(('::', port))
    listener.listen(1)
    print(f"Listening for incoming connections on port {port}...")
    conn, addr = listener.accept()
    print(f"Connected by {addr}")
    return conn

def connect_to_peer(peer_ip, port):
    """Function to try connecting to a peer."""
    time.sleep(2)  # Delay to ensure both parties are listening
    client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        client.connect((peer_ip, port))
        print(f"Connected to peer {peer_ip}")
        return client
    except:
        return None

def handle_connection(sock):
    """Handles incoming and outgoing messages."""
    def receive_messages(sock):
        while True:
            message = sock.recv(1024).decode('utf-8')
            print(f"Peer: {message}")

    # Start a thread to listen for messages from the peer
    threading.Thread(target=receive_messages, args=(sock,)).start()

    # Send messages
    while True:
        message = input("You: ")
        sock.send(message.encode('utf-8'))

def p2p_chat(peer_ip, port):
    # Try to listen for connections and connect to the peer simultaneously
    listener_thread = threading.Thread(target=listen_for_connections, args=(port,))
    listener_thread.start()

    sock = connect_to_peer(peer_ip, port)
    if not sock:
        # If failed to connect, wait for a peer to connect
        listener_thread.join()
        sock = listen_for_connections(port)

    handle_connection(sock)

if __name__ == "__main__":
    peer_ip = "201:e8c5:3538:87a3:aa54:7dfb:8008:fb2e"  # Replace with peer's Yggdrasil IP
    port = 12345
    p2p_chat(peer_ip, port)
