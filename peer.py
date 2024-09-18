import socket
import threading
import time

class PeerManager:
    def __init__(self, local_port, status_port):
        self.peers = {}  # Dictionary to store peer status and metadata
        self.local_port = local_port
        self.status_port = status_port
        self.lock = threading.Lock()  # To prevent race conditions when updating peer status
    
    def add_peer(self, peer_ip, chat_port):
        """Add a new peer to the manager."""
        with self.lock:
            self.peers[peer_ip] = {
                'chat_port': chat_port,
                'status': 'unknown'
            }
    
    def remove_peer(self, peer_ip):
        """Remove a peer from the manager."""
        with self.lock:
            if peer_ip in self.peers:
                del self.peers[peer_ip]

    def update_peer_status(self, peer_ip, status):
        """Update the status of a peer."""
        with self.lock:
            if peer_ip in self.peers:
                self.peers[peer_ip]['status'] = status
    
    def get_peer_status(self, peer_ip):
        """Get the status of a peer."""
        with self.lock:
            return self.peers.get(peer_ip, {}).get('status', 'unknown')

    def check_status(self, peer_ip):
        """Ping the peer to check if it is available or busy."""
        client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # Using UDP for status check
        try:
            client.sendto(b'status', (peer_ip, self.status_port))
            data, _ = client.recvfrom(1024)
            return data.decode('utf-8')
        except socket.error as e:
            print(f"Error checking status: {e}")
            return 'unknown'
        finally:
            client.close()

    def broadcast_status_updates(self):
        """Periodically broadcast status updates to all peers."""
        while True:
            for peer_ip in list(self.peers):
                status = self.check_status(peer_ip)
                self.update_peer_status(peer_ip, status)
            time.sleep(5)  # Status update interval
    
    def start_status_server(self):
        """Start the server to respond to status requests from other peers."""
        status_server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        status_server.bind(('::', self.status_port))
        print(f"Status server is listening on port {self.status_port}...")
        
        while True:
            data, addr = status_server.recvfrom(1024)
            print(f"Received status request from {addr}")
            if data.decode('utf-8') == 'status':
                status = 'available'  # For now, always available. Can be dynamic.
                status_server.sendto(status.encode('utf-8'), addr)

    def send_message(self, peer_ip, message):
        """Send a message to a peer."""
        peer_data = self.peers.get(peer_ip)
        if not peer_data or peer_data['status'] != 'available':
            print(f"Cannot send message. Peer {peer_ip} is not available.")
            return
        
        chat_port = peer_data['chat_port']
        client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        try:
            client.connect((peer_ip, chat_port))
            client.send(message.encode('utf-8'))
            print(f"Message sent to {peer_ip}")
        except socket.error as e:
            print(f"Error sending message to {peer_ip}: {e}")
        finally:
            client.close()

    def start_chat_server(self):
        """Start the chat server to handle incoming messages."""
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('::', self.local_port))
        server.listen(5)
        print(f"Chat server is listening on port {self.local_port}...")
        
        while True:
            conn, addr = server.accept()
            print(f"Connected by {addr}")
            threading.Thread(target=self.handle_incoming_message, args=(conn,)).start()

    def handle_incoming_message(self, conn):
        """Handle incoming messages."""
        while True:
            message = conn.recv(1024).decode('utf-8')
            if not message:
                print("Connection closed.")
                break
            print(f"Received message: {message}")
        conn.close()

    def start(self):
        # Start the status server and chat server
        threading.Thread(target=self.start_status_server, daemon=True).start()
        threading.Thread(target=self.start_chat_server, daemon=True).start()

        # Broadcast status updates in the background
        threading.Thread(target=self.broadcast_status_updates, daemon=True).start()