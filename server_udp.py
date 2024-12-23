import socket
import os
import time
import hashlib

HOST = '127.0.0.1'
PORT = 12345

FILE_LIST_PATH = 'file_list.txt'

BUFFER = 65536

def get_file_list():
    if not os.path.exists(FILE_LIST_PATH):
        return []
    file_list = {}
    with open(FILE_LIST_PATH, "r") as f:
        for line in f:
            name, size = line.strip().split(" ")
            file_list[name] = int(size)
    return file_list

def hash_data(data):
    return hashlib.md5(data).hexdigest()

def handle_client(server_socket, file_list):
    while True:
        request, client_addr = server_socket.recvfrom(BUFFER)
        request = request.decode()

        command, *args = request.split(" ")
        if command == "LIST":
            file_list_str = "\n".join([f"{name} {size}" for name, size in file_list.items()])
            server_socket.sendto(file_list_str.encode(), client_addr)

        elif command == "DOWNLOAD":
            offset, size, file_name, _ = args
            offset = int(offset)
            size = int(size)

            if file_name not in file_list:
                print("[SERVER-UDP] File not found")
                server_socket.sendto("ERROR".encode(), client_addr)
                continue

            with open(file_name, "rb") as f:
                f.seek(offset)
                data = f.read(size)
                checksum = hash_data(data)
                server_socket.sendto(data, client_addr)
                server_socket.sendto(checksum.encode(), client_addr)
        
        elif command == "EXIT":
            print("[SERVER-UDP] Closing connection with ", client_addr)
            break
        else:
            print("[SERVER-UDP] Unknown command")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    file_list = get_file_list()

    try:
        print("[SERVER-UDP] Server is listening on ", (HOST, PORT))
        while True:
            handle_client(server_socket, file_list)
    except Exception as e:
        print("[SERVER-UDP] Error: ", e)
    except KeyboardInterrupt:
        print("[SERVER-UDP] Server closed")
        server_socket.close()

if __name__ == "__main__":
    main()



                




