import socket
import os
import threading
import time

# Define the host and port
HOST = "192.168.170.240"
PORT = 12345

# Define the input file path and buffer size
INPUT_FILE_PATH = "input.txt"
BUFFER = 65536

# Define the lock for progress printing
progress_lock = threading.Lock()

def download_chunk(file_name, offset, chunk_size, output_file, part, part_progress):
    global total_downloaded
    try:
        #Create a new socket for each chunk
        thread_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        thread_socket.connect((HOST, PORT))
        command = f"DOWNLOAD {file_name} {offset} {chunk_size[part]}"
        thread_socket.sendall(command.encode())
        # Receive the data in chunks and print the progress
        received = b""
        while len(received) < chunk_size[part]:
            data = thread_socket.recv(BUFFER)
            if not data:
                break
            received += data
            part_progress[part] += len(data)
            print_progress(file_name, part_progress, chunk_size)    
        with open(output_file, "r+b") as f:
            f.seek(offset)
            f.write(received)
    except Exception as e:
        print("[CLIENT-TCP] Error: ", e)

def print_progress(file_name, part_progress, chunk_size):
    progress_lines = []
    for i in range(4):
        percentage = (part_progress[i] / chunk_size[i]) * 100
        progress_lines.append(f"Downloading {file_name} part {i+1} .... {percentage:.2f}%")
    with progress_lock:
        print("\033[H\033[J", end="")  # Clear the screen
        print("\n".join(progress_lines))

def download_file(client_socket, file_name):
    global total_downloaded
    total_downloaded = 0
    chunk_size = []
    part_progress = []
    THREAD_COUNT = 4

    # Receive the file list from the server
    client_socket.sendall(f"LIST".encode())
    file_list = client_socket.recv(BUFFER).decode().split("\n")
    file_dict = dict([line.split(" ") for line in file_list])

    if file_name not in file_dict:
        print("[CLIENT-TCP] File not exists")
        return
    
    file_size = int(file_dict[file_name])
    print("[CLIENT-TCP] Start download ", file_name)

    output_file = f"downloaded_{file_name}"
    with open(output_file, "wb") as f:
        f.truncate(file_size)
    
    # Create threads for each chunk
    threads = []
    for i in range(THREAD_COUNT):
        file_part = i
        offset = i * (file_size // THREAD_COUNT)
        part_size = file_size // THREAD_COUNT
        chunk_size.append(part_size)
        part_progress.append(0)

        if i == THREAD_COUNT - 1:
            chunk_size[i] = file_size - offset

        thread = threading.Thread(
            target=download_chunk,
            args=(file_name, offset, chunk_size, output_file, file_part, part_progress)
        )
        threads.append(thread)
        
    for thread in threads:
        thread.start()
        time.sleep(0.01)

    for thread in threads:
        thread.join()

    print("\n[CLIENT-TCP] Download complete ", file_name)
    print("List of files on server: ")
    for p in file_dict:
        print(p)

def scan_input_file():
    if not os.path.exists(INPUT_FILE_PATH):
        return []
    with open(INPUT_FILE_PATH, "r") as f:
        files = [line.strip() for line in f if line.strip()]
    return files

def main():
    # Connect to the server
    print("[CLIENT-TCP] Connecting to server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("[CLIENT-TCP] Connected to server at ", (HOST, PORT))

    download_files = []

    try:
        while True:
            file_to_download = scan_input_file()
            for file_name in file_to_download:
                if file_name not in download_files:
                    download_files.append(file_name)
                    download_file(client_socket, file_name)
            time.sleep(5)
    except KeyboardInterrupt:
        client_socket.sendall(f"EXIT".encode())
        print("[CLIENT-TCP] Closing connection")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()  







    



