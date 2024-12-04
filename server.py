import socket
import threading
import os

# File chứa danh sách các file Server có
FILE_LIST_PATH = "file_list.txt"

# Hàm tải danh sách file từ file text
def load_file_list():
    file_list = {}
    with open(FILE_LIST_PATH, "r") as f:
        for line in f:
            name, size = line.strip().split()
            file_list[name] = int(size)
    return file_list

# Hàm xử lý mỗi Client
def handle_client(client_socket, client_address, file_list):
    print(f"[SERVER-TCP] Kết nối từ: {client_address}")
    while True:
        try:
            # Nhận yêu cầu từ Client
            request = client_socket.recv(1024).decode()
            if not request:
                break
            command, *args = request.split()

            if command == "LIST":
                # Gửi danh sách file cho Client
                response = "\n".join([f"{name} {size}" for name, size in file_list.items()])
                client_socket.sendall(response.encode())

            elif command == "DOWNLOAD":
                # Nhận yêu cầu tải file
                filename, offset, chunk_size = args
                offset = int(offset)
                chunk_size = int(chunk_size)

                if filename not in file_list:
                    client_socket.sendall(b"ERROR: File not found")
                    continue

                # Đọc và gửi chunk
                with open(filename, "rb") as f:
                    f.seek(offset)
                    data = f.read(chunk_size)
                    client_socket.sendall(data)

            elif command == "EXIT":
                print(f"[SERVER-TCP] Client {client_address} đã ngắt kết nối.")
                break
        except Exception as e:
            print(f"[SERVER-TCP] Lỗi: {e}")
            break
    client_socket.close()

# Chạy Server TCP
def main():
    HOST = "192.168.150.5"
    PORT = 12345

    # Tải danh sách file
    file_list = load_file_list()

    # Tạo Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER-TCP] Đang lắng nghe tại {HOST}:{PORT}...")

    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, file_list))
        client_thread.start()

if __name__ == "__main__":
    main()