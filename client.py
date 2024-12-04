import socket
import time
import os

# File input chứa danh sách file cần tải
INPUT_FILE_PATH = "input.txt"

# Hàm tải file từ Server
def download_file(client_socket, filename):
    CHUNK_SIZE = 1024

    # Gửi yêu cầu danh sách file
    client_socket.sendall(b"LIST")
    file_list = client_socket.recv(4096).decode()

    # Kiểm tra file
    if filename not in file_list:
        print(f"[CLIENT-TCP] File {filename} không tồn tại trên Server.")
        return

    print(f"[CLIENT-TCP] Bắt đầu tải {filename}...")

    # Tải file
    with open(f"downloaded_{filename}", "wb") as f:
        file_size = int(file_list.split(filename)[1])
        offset = 0

        while offset < file_size:
            command = f"DOWNLOAD {filename} {offset} {CHUNK_SIZE}"
            client_socket.sendall(command.encode())
            data = client_socket.recv(CHUNK_SIZE)
            f.write(data)
            offset += len(data)
            print(f"[CLIENT-TCP] Tải {filename}... {offset / file_size:.2%}")

    print(f"[CLIENT-TCP] Tải xong {filename}")

# Hàm đọc file input.txt
def scan_input_file():
    if not os.path.exists(INPUT_FILE_PATH):
        with open(INPUT_FILE_PATH, "w") as f:
            pass
    with open(INPUT_FILE_PATH, "r") as f:
        files = [line.strip() for line in f if line.strip()]
    return files

# Chạy Client TCP
def main():
    HOST = "192.168.178.240"
    PORT = 12345
    print(f"Dng ket noi")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"[CLIENT-TCP] Đã kết nối tới Server tại {HOST}:{PORT}.")

    downloaded_files = []

    try:
        while True:
            files_to_download = scan_input_file()
            for filename in files_to_download:
                if filename not in downloaded_files:
                    download_file(client_socket, filename)
                    downloaded_files.append(filename)
            time.sleep(5)
    except KeyboardInterrupt:
        print("[CLIENT-TCP] Ngắt kết nối với Server.")
        client_socket.sendall(b"EXIT")
        client_socket.close()
        
if __name__ == "__main__":
    main()