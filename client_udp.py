import socket
import os
import time
import threading
import hashlib

HOST = '127.0.0.1'
PORT = 12345

INPUT_FILE_PATH = 'input.txt'

BUFFER = 65536

progress_lock = threading.Lock()

def scan_input_file():
    if not os.path.exists(INPUT_FILE_PATH):
        return []
    with open(INPUT_FILE_PATH, "r") as f:
        files = [line.strip() for line in f if line.strip()]
    return files

def hash_data(data):
    return hashlib.md5(data).hexdigest() 

def download_file(client_socket, file_name):
    THREAD_COUNT = 4

    request = f"LIST"
    client_socket.sendto(request.encode(), (HOST, PORT))
    data, _ = client_socket.recvfrom(BUFFER)
    data = data.decode()

    file_list = data.split("\n")
    file_dict = dict([line.split(" ") for line in file_list])

    if file_name not in file_dict:
        print("File not found")
        return
    
    file_size = int(file_dict[file_name])
    print("[CLIENT-UDP] Start download ", file_name)

    output_file = f"downloaded_{file_name}"
    with open(output_file, "wb") as f:
        f.truncate(file_size)
    
    # Create threads for each chunk
    threads = []
    chunk_size = []
    part_progress = []
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

    print("[CLIENT-UDP] Downloaded ", file_name, " completed")
    print("File list: ")
    for p in file_dict:
        print(p)
def download_chunk(file_name, offset, chunk_size, output_file, file_part, part_progress):
    thread_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while part_progress[file_part] < chunk_size[file_part]:
        size_to_download = min(30000, chunk_size[file_part] - part_progress[file_part])
        request = f"DOWNLOAD {offset} {size_to_download} {file_name}"
        checksum = hash_data(request.encode())
        request = f"{request} {checksum}"
        thread_socket.sendto(request.encode(), (HOST, PORT))
        data, _ = thread_socket.recvfrom(BUFFER)
        checksum, _ = thread_socket.recvfrom(BUFFER)
        if checksum.decode() != hash_data(data):
            thread_socket.sendto(request.encode(), (HOST, PORT))
            data, _ = thread_socket.recvfrom(BUFFER)
            checksum, _ = thread_socket.recvfrom(BUFFER)

        with open(output_file, "r+b") as f:
            f.seek(offset)
            f.write(data)
        
        offset += size_to_download
        part_progress[file_part] += size_to_download
        print_progress(file_name, part_progress, chunk_size)

def print_progress(file_name, part_progress, chunk_size):
    progress_lines = []
    for i in range(4):
        percentage = (part_progress[i] / chunk_size[i]) * 100
        progress_lines.append(f"Downloading {file_name} part {i+1} .... {percentage:.2f}%")
    with progress_lock:
        print("\033[H\033[J", end="")  # Clear the screen
        print("\n".join(progress_lines))    

def main():
    # Connect to the server
    print("[CLIENT-UDP] Connecting to server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[CLIENT-UDP] Connected to server at ", (HOST, PORT))
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
        client_socket.sendto(f"EXIT".encode(), (HOST, PORT))
        print("[CLIENT-UDP] Closing connection")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()   