import socket
import threading
import os

# File chứa danh sách các file Server có
FILE_LIST_PATH = "file_list.txt"

# Danh sách các kết nối client đang hoạt động
active_connections = []

# Cấu hình UDP
HOST = "192.168.81.5"
PORT = 12345
BUFFER_SIZE = 4096

# Hàm tải danh sách file từ file text
def load_file_list():
    file_list = {}
    with open(FILE_LIST_PATH, "r") as f:
        for line in f:
            name, size = line.strip().split()
            file_list[name] = int(size)
    return file_list

# Hàm xử lý mỗi Client
def handle_client(server_socket, client_address, file_list):
    print(f"[SERVER-UDP] Kết nối từ: {client_address}")
    active_connections.append(client_address)  # Thêm địa chỉ vào danh sách kết nối
    try:
        while True:
            # Nhận yêu cầu từ Client
            request, addr = server_socket.recvfrom(BUFFER_SIZE)
            if not request:
                break
            command, *args = request.decode().split()

            if command == "LIST":
                # Gửi danh sách file cho Client
                response = "\n".join([f"{name} {size}" for name, size in file_list.items()])
                server_socket.sendto(b'ACK' + response.encode(), client_address)

            elif command == "DOWNLOAD":
                # Nhận yêu cầu tải file
                filename, offset, chunk_size = args
                offset = int(offset)
                chunk_size = int(chunk_size)

                if filename not in file_list:
                    server_socket.sendto(b"ERROR: File not found", client_address)
                    continue

                # Đọc và gửi chunk
                with open(filename, "rb") as f:
                    f.seek(offset)
                    data = f.read(chunk_size)
                    server_socket.sendto(b'ACK' + data, client_address)

    except Exception as e:
        print(f"[SERVER-UDP] Lỗi: {e}")
    finally:
        active_connections.remove(client_address)  # Gỡ địa chỉ khỏi danh sách kết nối

# Chạy Server UDP
def main():
    # Tải danh sách file
    file_list = load_file_list()

    # Tạo Server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"[SERVER-UDP] Đang lắng nghe tại {HOST}:{PORT}...")

    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        client_thread = threading.Thread(target=handle_client, args=(server_socket, client_address, file_list))
        client_thread.start()

if __name__ == "__main__":
    main()