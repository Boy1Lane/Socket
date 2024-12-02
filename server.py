import socket
#123
HOST = '192.168.150.5'  # Địa chỉ localhost
PORT = 65431        # Cổng để lắng nghe

# Tạo socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)  # Lắng nghe 1 kết nối cùng lúc
print("Server is ready and waiting for a connection...")

while True:
    conn, addr = s.accept()  # Chấp nhận kết nối
    print('Connected by', addr)
    try:
        while True:
            # Nhận dữ liệu từ client
            data = conn.recv(1024)
            if not data:
                break
            str_data = data.decode("utf8")
            print("Client: " + str_data)

            if str_data.lower() == "quit":  # Thoát nếu client gửi "quit"
                print("Client disconnected.")
                break

            # Gửi phản hồi từ server
            msg = input("Server: ")
            conn.sendall(msg.encode("utf8"))

            if msg.lower() == "quit":  # Server kết thúc nếu gửi "quit"
                print("Server is shutting down.")
                conn.close()
                s.close()
                exit()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        conn.close()
