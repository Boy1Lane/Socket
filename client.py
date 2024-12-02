import socket

HOST = '192.168.150.5'  # Địa chỉ server
PORT = 65431        # Cổng server đang lắng nghe

# Tạo socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
print('Connecting to {} port {}'.format(*server_address))
s.connect(server_address)

try:
    while True:
        # Gửi dữ liệu từ client
        msg = input('Client: ')
        s.sendall(msg.encode("utf8"))

        if msg.lower() == "quit":  # Client thoát nếu gửi "quit"
            print("Closing connection.")
            break

        # Nhận phản hồi từ server
        data = s.recv(1024)
        if not data:
            print("Server disconnected.")
            break
        print('Server:', data.decode("utf8"))
finally:
    s.close()
