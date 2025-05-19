import socket
import sys

def run_client(server_host, server_port, filename):
    """
    Terhubung ke server, mengirimkan request GET, dan menampilkan response.
    """

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))
    except socket.error as e:
        print(f"Tidak dapat terhubung ke server: {e}")
        return

    request = f"GET /{filename} HTTP/1.1\r\nHost: {server_host}:{server_port}\r\nConnection: close\r\n\r\n"
    client_socket.sendall(request.encode())

    response = b''
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            response += data
    except socket.error as e:
        print(f"Error menerima data: {e}")

    client_socket.close()

    print("Response dari server:\n", response.decode('utf-8', errors='ignore'))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python client.py server_host server_port filename")
    else:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])
        filename = sys.argv[3]
        run_client(server_host, server_port, filename)