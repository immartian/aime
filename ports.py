import socket

def scan_ports(ip, start_port, end_port):
    open_ports = []
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"Port {port} is open.")
            open_ports.append(port)
        else:
            print(f"Port {port} is closed.")
        sock.close()
    return open_ports

if __name__ == "__main__":
    target_ip = "201:e8c5:3538:87a3:aa54:7dfb:8008:fb2e"
    start_port = 10000
    end_port = 10100
    open_ports = scan_ports(target_ip, start_port, end_port)
    print(f"Open ports: {open_ports}")
