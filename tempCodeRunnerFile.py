import socket
import json
import os
import time
import struct
import threading
from pathlib import Path

class FileClient:
    def __init__(self, server_host='192.168.81.240', server_port=5000):
        self.server_address = (server_host, server_port)
        self.buffer_size = 1024
        self.download_path = "downloads"
        self.chunks_per_file = 4
        self.seq_number = 0
        Path(self.download_path).mkdir(exist_ok=True)
        
        # Initialize UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def get_file_list(self):
        request = json.dumps({"type": "list"}).encode()
        self.sock.sendto(request, self.server_address)
        data, _ = self.sock.recvfrom(self.buffer_size)
        return json.loads(data.decode())
    
    def create_ack(self, seq_number):
        return struct.pack('!I', seq_number)
    
    def receive_with_ack(self, sock):
        while True:
            try:
                data, addr = sock.recvfrom(self.buffer_size)
                seq_number, is_last, chunk_data = self.extract_packet(data)
                
                # Send ACK
                ack = self.create_ack(seq_number)
                sock.sendto(ack, addr)
                
                return chunk_data, is_last
            except socket.timeout:
                continue
    
    def extract_packet(self, packet):
        seq_number, is_last = struct.unpack('!IB', packet[:5])
        return seq_number, bool(is_last), packet[5:]
    
    def download_chunk(self, filename, chunk_start, chunk_size, file_lock):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        
        request = json.dumps({
            "type": "download",
            "filename": filename,
            "chunk_start": chunk_start,
            "chunk_size": chunk_size
        }).encode()
        
        sock.sendto(request, self.server_address)
        
        temp_chunk = []
        bytes_received = 0
        
        while bytes_received < chunk_size:
            chunk_data, is_last = self.receive_with_ack(sock)
            temp_chunk.append(chunk_data)
            bytes_received += len(chunk_data)
            
            progress = (bytes_received / chunk_size) * 100
            print(f"Downloading {filename} chunk {chunk_start//chunk_size + 1} ... {progress:.2f}%")
            
            if is_last:
                break
        
        with file_lock:
            with open(f"{self.download_path}/{filename}", 'rb+' if os.path.exists(f"{self.download_path}/{filename}") else 'wb') as f:
                f.seek(chunk_start)
                f.write(b''.join(temp_chunk))
        
        sock.close()
    
    def download_file(self, filename, file_size):
        chunk_size = file_size // self.chunks_per_file
        threads = []
        file_lock = threading.Lock()
        
        # Create empty file
        with open(f"{self.download_path}/{filename}", 'wb') as f:
            f.truncate(file_size)
        
        for i in range(self.chunks_per_file):
            chunk_start = i * chunk_size
            actual_chunk_size = chunk_size if i < self.chunks_per_file - 1 else file_size - chunk_start
            
            thread = threading.Thread(
                target=self.download_chunk,
                args=(filename, chunk_start, actual_chunk_size, file_lock)
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
            
        print(f"Download completed: {filename}")
    
    def run(self):
        while True:
            try:
                files = self.get_file_list()
                print("\nAvailable files:")
                for filename, size in files.items():
                    print(f"{filename}: {size//(1024*1024)}MB")
                
                filename = input("\nEnter filename to download (or 'quit' to exit): ")
                if filename.lower() == 'quit':
                    break
                    
                if filename in files:
                    self.download_file(filename, files[filename])
                else:
                    print("File not found!")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    client = FileClient()
    client.run()