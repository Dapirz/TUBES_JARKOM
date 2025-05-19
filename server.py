import socket
import threading
import os
import mimetypes

# Konfigurasi server
HOST = '127.0.0.1'
PORT = 8080
WEB_ROOT = '.'
FILE_NOT_FOUND_PAGE = '404.html'  # Nama file 404 Anda

def handle_request(client_socket):
    """Menangani satu permintaan HTTP."""

    try:
        request_data = client_socket.recv(1024).decode('utf-8')
    except ConnectionResetError:
        print("Koneksi terputus oleh klien.")
        client_socket.close()
        return
    if not request_data:
        client_socket.close()
        return

    print("Menerima permintaan:\n", request_data)

    try:
        path = request_data.split(' ')[1]
        if path == '/':
            path = '/index.html'
    except IndexError:
        path = '/index.html'

    filepath = os.path.join(WEB_ROOT, path.lstrip('/'))
    filepath = os.path.normpath(filepath)

    if not os.path.exists(filepath) or os.path.isdir(filepath):
        # File tidak ditemukan, sajikan 404.html
        filepath = os.path.join(WEB_ROOT, FILE_NOT_FOUND_PAGE)
        if not os.path.exists(filepath):
            # Jika 404.html juga tidak ada, kirim pesan teks
            response = b'HTTP/1.1 404 Not Found\r\n'
            response += b'Content-Type: text/plain\r\n'
            response += b'\r\n'
            response += b'File Not Found'
        else:
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                content_type, _ = mimetypes.guess_type(filepath)
                if content_type is None:
                    content_type = 'application/octet-stream'
                response = b'HTTP/1.1 404 Not Found\r\n'  # Tetap 404 status
                response += b'Content-Type: ' + content_type.encode() + b'\r\n'
                response += b'Content-Length: ' + str(len(content)).encode() + b'\r\n'
                response += b'\r\n'
                response += content
            except Exception as e:
                response = b'HTTP/1.1 500 Internal Server Error\r\n'
                response += b'Content-Type: text/plain\r\n'
                response += b'\r\n'
                response += str(e).encode()
    else:
        # File ditemukan, sajikan file yang diminta
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            content_type, _ = mimetypes.guess_type(filepath)
            if content_type is None:
                content_type = 'application/octet-stream'
            response = b'HTTP/1.1 200 OK\r\n'
            response += b'Content-Type: ' + content_type.encode() + b'\r\n'
            response += b'Content-Length: ' + str(len(content)).encode() + b'\r\n'
            response += b'\r\n'
            response += content
        except Exception as e:
            response = b'HTTP/1.1 500 Internal Server Error\r\n'
            response += b'Content-Type: text/plain\r\n'
            response += b'\r\n'
            response += str(e).encode()

    client_socket.sendall(response)
    client_socket.close()

def handle_client(client_socket, client_address):
    """Menangani satu klien dalam thread."""

    print(f"Koneksi dari {client_address}")
    handle_request(client_socket)

def start_server():
    """Mulai server web multithread."""

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Server berjalan di http://{HOST}:{PORT}/")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()