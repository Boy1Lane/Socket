import socket
import os
import time

# Cấu hình client
SERVER_HOST = '192.168.170.240'  # IP của server
SERVER_PORT = 5001               # Cổng server
BUFFER_SIZE = 4096               # Kích thước bộ đệm
SEPARATOR = "<SEPARATOR>"        # Ký tự phân cách

# Đường dẫn file cần gửi
filename = "file1.docx"
filesize = os.path.getsize(filename)

# Tạo kết nối tới server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"[*] Đang kết nối tới {SERVER_HOST}:{SERVER_PORT}")
client_socket.connect((SERVER_HOST, SERVER_PORT))
print("[+] Kết nối thành công.")
time.sleep(0.2)

# Gửi thông tin file (metadata)
file_info = f"{filename}{SEPARATOR}{filesize}"
client_socket.send(file_info.encode('utf-8'))

# Gửi nội dung file dưới dạng nhị phân
with open(filename, "rb") as f:
    while True:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            break
        client_socket.sendall(bytes_read)

print(f"[+] File {filename} đã được gửi thành công.")
client_socket.close()
