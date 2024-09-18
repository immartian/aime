import socket
import threading
import time

def listen_for_connections(local_port, conn_event, connection_holder):
    """Function to listen for incoming connections."""
    listener = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('::', local_port))
    listener.listen(1)
    print(f"Listening for incoming connections on port {local_port}...")

    # Accept connection when it arrives
    conn, addr = listener.accept()
    print(f"Connected by {addr}")
    connection_holder['conn'] = conn
    conn_event.set()  # Notify the main thread that connection is established
    listener.close()

def connect_to_peer(peer_ip, remote_port, conn_event, connection_holder):
    """Function to try connecting to a peer."""
    while not conn_event.is_set():  # Retry until connected
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        try:
            print(f"Attempting to connect to {peer_ip}:{remote_port}...")
            client.connect((peer_ip, remote_port))
            print(f"Connected to peer {peer_ip}:{remote_port}")
            connection_holder['conn'] = client
            conn_event.set()  # Notify that the connection is established
            break
        except socket.error as e:
            print(f"Connection to {peer_ip}:{remote_port} failed: {e}")
            time.sleep(2)  # Wait and retry if connection fails
        finally:
            client.close()

def handle_connection(sock):
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
    """Main function to handle peer-to-peer chat."""
    # Event to signal when a connection is established
    conn_event = threading.Event()
    connection_holder = {'conn': None}

    # Start listener thread (server role)
    listener_thread = threading.Thread(target=listen_for_connections, args=(local_port, conn_event, connection_holder))
    listener_thread.start()

    # Start connection thread (client role)
    connect_thread = threading.Thread(target=connect_to_peer, args=(peer_ip, remote_port, conn_event, connection_holder))
    connect_thread.start()

    # Wait for connection to be established (either as server or client)
    conn_event.wait()

    # Handle communication once the connection is made
    sock = connection_holder['conn']
    handle_connection(sock)

if __name__ == "__main__":
    peer_ip = "201:e8c5:3538:87a3:aa54:7dfb:8008:fb2e"  # Replace with peer's Yggdrasil IP
    #peer_ip = "200:170:d1b:9552:79e7:2726:50aa:4f48"  # Replace with peer's Yggdrasil IP
    local_port = 12345  # The port we will listen on
    remote_port = 12346  # The port our peer is listening on

    p2p_chat(peer_ip, local_port, remote_port)

