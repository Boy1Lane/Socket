import socket
import os

# Chạy Client UDP
def download_file_udp(server_address, filename):
    CHUNK_SIZE = 1024
    offset = 0

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open(f"downloaded_{filename}", "wb") as f:
        while True:
            command = f"DOWNLOAD {filename} {offset}"
            client.sendto(command.encode(), server_address)

            # Nhận chunk
            data, _ = client.recvfrom(CHUNK_SIZE)
            if not data:
                break
            f.write(data)
            offset += len(data)
            print(f"[CLIENT-UDP] Tải {filename}... {offset} bytes")

    print(f"[CLIENT-UDP] Tải xong {filename}")


def main():
    SERVER_HOST = "192.168.178.240"
    SERVER_PORT = 12346
    server_address = (SERVER_HOST, SERVER_PORT)

    filename = input("[CLIENT-UDP] Nhập tên file cần tải: ")
    download_file_udp(server_address, filename)


if __name__ == "__main__":
    main()
