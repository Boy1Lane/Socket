import socket
import os
import threading

# Path to the file list
FILE_LIST_PATH = "file_list.txt"

# Server address
HOST = "127.0.0.1"
PORT = 12345

# List of active connections
active_connections = []

# Buffer size
BUFFER = 65536

def load_file_list():
    file_list={}
    if not os.path.exists(FILE_LIST_PATH):
        return []
    with open(FILE_LIST_PATH, "r") as f:
        for line in f:
            name, size = line.strip().split(" ")
            file_list[name] = int(size)
    return file_list

def handle_client(client_socket, client_addr, file_list):
    print("[SERVER-TCP] New connection from ", client_addr)
    active_connections.append(client_socket)

    try:
        while True:
            request = client_socket.recv(BUFFER).decode()
            if not request:
                break
            command, *args = request.split(" ")

            # Handle the command
            if command == "LIST":
                response = "\n".join([f"{name} {size}" for name, size in file_list.items()])
                client_socket.sendall(response.encode())
                
            elif command == "DOWNLOAD":
                file_name, offset, chunk_size = args
                offset = int(offset)
                chunk_size = int(chunk_size)

                if file_name not in file_list:
                    client_socket.sendall(b"ERROR: File not found".encode())
                    continue

                with open(file_name, "rb") as f:
                    f.seek(offset)
                    data = f.read(chunk_size)
                    client_socket.sendall(data)

            elif command == "EXIT":
                print("[SERVER-TCP] Closing connection with ", client_addr)
                break
    except Exception as e:
        print("[SERVER-TCP] Error: ", e)    
    finally:
        client_socket.close()
        active_connections.remove(client_socket)

def main():
    file_list = load_file_list()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("[SERVER-TCP] Server started at ", (HOST, PORT))

    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr, file_list))
            client_thread.start()
    except Exception as e:
        print("[SERVER-TCP] Error: ", e)
    finally:
        for connection in active_connections:
            connection.close()
        server_socket.close()
        
if __name__ == "__main__":
    main()
                
                
                

