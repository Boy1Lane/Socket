import socket
import threading
import os
import time

# File input chứa danh sách file cần tải
INPUT_FILE_PATH = "input.txt"

# Biến chia sẻ để theo dõi tiến độ tải
progress_lock = threading.Lock()
total_downloaded = 0

# Hàm tải một chunk của file
def download_chunk(client_socket, filename, offset, chunk_size, output_file, file_part, part_progress, total_size):
    global total_downloaded
    try:
        command = f"DOWNLOAD {filename} {offset} {chunk_size[file_part]}"
        client_socket.sendall(command.encode())
        data = client_socket.recv(chunk_size[file_part])
        
        # Ghi chunk vào file
        with open(output_file, "r+b") as f:
            f.seek(offset)
            f.write(data)

        # Cập nhật tiến độ cho phần hiện tại
        with progress_lock:
            total_downloaded += len(data)
            part_progress[file_part] += len(data)
            part_percent = (part_progress[file_part] / chunk_size[file_part]) * 100
            total_percent = (total_downloaded / total_size) * 100
            print(f"[CLIENT-TCP] Đang tải {filename} - Phần {file_part + 1}: {part_percent:.2f}%")
            print(f"[CLIENT-TCP] Tổng tiến độ tải {filename}: {total_percent:.2f}%")
    except Exception as e:
        print(f"[CLIENT-TCP] Lỗi khi tải chunk {offset}-{offset+chunk_size[file_part]} của {filename}: {e}")

# Hàm tải file từ Server
def download_file(client_socket, filename):
    global total_downloaded
    total_downloaded = 0
    chunk_size = []
    part_progress = []
    THREAD_COUNT = 4   # Số luồng tải song song
    # Gửi yêu cầu danh sách file
    client_socket.sendall(b"LIST")
    file_list = client_socket.recv(4096).decode()

    # Kiểm tra file
    file_dict = dict(line.split() for line in file_list.split("\n") if line.strip())
    if filename not in file_dict:
        print(f"[CLIENT-TCP] File {filename} không tồn tại trên Server.")
        return

    file_size = int(file_dict[filename])
    print(f"[CLIENT-TCP] Bắt đầu tải {filename} (kích thước: {file_size} bytes)...")

    # Tạo file rỗng để ghi dữ liệu
    output_file = f"downloaded_{filename}"
    with open(output_file, "wb") as f:
        f.truncate(file_size)

    # Tạo các luồng để tải đồng thời các phần của file
    threads = []
    for i in range(THREAD_COUNT):
        file_part = i
        offset = i * (file_size // THREAD_COUNT)
        part_size = file_size // THREAD_COUNT
        chunk_size.append(part_size)
        part_progress.append(0)

        # Điều chỉnh kích thước chunk cuối cùng nếu không chia hết
        if i == THREAD_COUNT - 1:
            chunk_size[i] = file_size - offset

        thread = threading.Thread(
            target=download_chunk,
            args=(client_socket, filename, offset, chunk_size, output_file, file_part, part_progress, file_size)
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.3)

    # Chờ tất cả các luồng hoàn thành
    for thread in threads:
        thread.join()

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
    HOST = "192.168.81.240"
    PORT = 12345
    print("[CLIENT-TCP] Đang kết nối...")
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
