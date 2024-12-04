import socket

# Chạy Server UDP
def main():
    HOST = "127.0.0.1"
    PORT = 12346
    CHUNK_SIZE = 1024

    # Tạo UDP Socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    print(f"[SERVER-UDP] Đang lắng nghe tại {HOST}:{PORT}...")

    while True:
        try:
            data, client_address = server.recvfrom(1024)
            command, filename, offset = data.decode().split()
            offset = int(offset)

            # Gửi chunk
            with open(filename, "rb") as f:
                f.seek(offset)
                chunk = f.read(CHUNK_SIZE)
                server.sendto(chunk, client_address)
        except Exception as e:
            print(f"[SERVER-UDP] Lỗi: {e}")


if __name__ == "__main__":
    main()