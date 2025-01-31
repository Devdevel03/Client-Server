import socket
import sys
import os
import time

# Function to download a file from the server (receive the entire file at once)
def download_file(server_ip, server_port, filename, save_dir):
    try:
        # Connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")

        # Check and adjust the buffer size
        default_buffer_size = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        print(f"Default socket receive buffer size: {default_buffer_size} bytes")

        # You can set a larger buffer size here (e.g., 128 KB)
        new_buffer_size = 128 * 1024  # 128 KB
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, new_buffer_size)
        print(f"Setting socket receive buffer size to: {new_buffer_size} bytes")

        # Send the filename to the server
        client_socket.send(filename.encode())

        # Receive the file size
        file_size_data = client_socket.recv(1024)
        try:
            file_size = int(file_size_data.decode().strip())
        except ValueError:
            print(f"Server error: {file_size_data.decode().strip()}")
            return False

        if file_size <= 0:
            print(f"Server error: Invalid file size {file_size}")
            return False

        print(f"Downloading {filename} ({file_size} bytes)")

        # Send acknowledgment to the server
        client_socket.send("READY".encode())

        # Receive the entire file data in one go (after receiving file size)
        file_data = b""  # Initialize an empty byte string
        while len(file_data) < file_size:
            # Receive in chunks, but combine them into a single byte string
            data = client_socket.recv(new_buffer_size)
            if not data:
                break
            file_data += data  # Append received data

        if len(file_data) == file_size:
            # Write the entire file to disk
            file_path = os.path.join(save_dir, filename)
            with open(file_path, "wb") as f:
                f.write(file_data)
            print(f"File {filename} downloaded successfully to {file_path}")
            return True
        else:
            print(f"File {filename} download incomplete. Received {len(file_data)}/{file_size} bytes")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

    finally:
        client_socket.close()


# Main function
def main():
    if len(sys.argv) != 5:
        print("Usage: python client.py n_A n_B IP_A IP_B")
        sys.exit(1)

    # Read command-line arguments
    n_a = int(sys.argv[1])
    n_b = int(sys.argv[2])
    ip_a = sys.argv[3]
    ip_b = sys.argv[4]

    # Save directory for downloaded files
    save_dir = "./downloads"
    os.makedirs(save_dir, exist_ok=True)

    total_files = 160
    counter = 1

    # Start time measurement
    start_time = time.time()  # Capture the start time

    while counter <= total_files:
        # Request files from server A
        for _ in range(n_a):
            if counter > total_files:
                break
            filename = f"s{counter:03}.m4s"
            if not download_file(ip_a, 5001, filename, save_dir):
                print(f"Failed to download {filename} from server A")
            counter += 1

        # Request files from server B
        for _ in range(n_b):
            if counter > total_files:
                break
            filename = f"s{counter:03}.m4s"
            if not download_file(ip_b, 5001, filename, save_dir):
                print(f"Failed to download {filename} from server B")
            counter += 1

    # End time measurement
    end_time = time.time()  # Capture the end time

    # Calculate the total time taken
    total_time = end_time - start_time

    # Print the total time taken for downloading all files
    print(f"\nTotal time taken to download all files: {total_time:.2f} seconds")


if __name__ == "__main__":
    main()
