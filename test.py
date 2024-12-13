import socket
import os
import time

INPUT_FILE_PATH = "input.txt"
HOST = "192.168.81.240"
PORT = 12345
BUFFER_SIZE = 4096
TIMEOUT = 2  # Thời gian chờ gói tin (giây)

# Gửi và nhận gói tin RDT
def send_recv_rdt(client_socket, message, expected_size):
    seq = 1
    while True:
        try:
            client_socket.sendto(message, (HOST, PORT))
            client_socket.settimeout(TIMEOUT)
            data, _ = client_socket.recvfrom(expected_size + 1024)
            received_seq, received_data = data.split(b" ", 1)
            received_seq = int(received_seq.decode())
            if received_seq == seq:
                client_socket.sendto(f"ACK {seq}".encode(), (HOST, PORT))
                return received_data
        except socket.timeout:
            print("[CLIENT-UDP] Timeout, gửi lại...")

# Tải file
def download_file(client_socket, filename):
    response = send_recv_rdt(client_socket, b"LIST", BUFFER_SIZE)
    file_list = response.decode()

    file_dict = dict(line.split() for line in file_list.split("\n") if line.strip())
    if filename not in file_dict:
        print(f"[CLIENT-UDP] File {filename} không tồn tại trên Server.")
        return

    file_size = int(file_dict[filename])
    print(f"[CLIENT-UDP] Tải {filename} (kích thước: {file_size} bytes)...")
    output_file = f"downloaded_{filename}"

    with open(output_file, "wb") as f:
        f.truncate(file_size)

    offset = 0
    chunk_size = BUFFER_SIZE - 32  # Trừ phần đầu gói tin
    while offset < file_size:
        chunk = min(chunk_size, file_size - offset)
        command = f"DOWNLOAD {filename} {offset} {chunk}"
        data = send_recv_rdt(client_socket, command.encode(), chunk)
        with open(output_file, "r+b") as f:
            f.seek(offset)
            f.write(data)
        offset += chunk
        print(f"[CLIENT-UDP] Đã tải {offset}/{file_size} bytes của {filename}")

    print(f"[CLIENT-UDP] Tải xong {filename}")

# Đọc danh sách file cần tải
def scan_input_file():
    if not os.path.exists(INPUT_FILE_PATH):
        with open(INPUT_FILE_PATH, "w") as f:
            pass
    with open(INPUT_FILE_PATH, "r") as f:
        files = [line.strip() for line in f if line.strip()]
    return files

# Chạy Client
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[CLIENT-UDP] Đã kết nối tới Server tại {HOST}:{PORT}.")

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
        print("[CLIENT-UDP] Ngắt kết nối với Server.")
        client_socket.close()

if __name__ == "__main__":
    main()
