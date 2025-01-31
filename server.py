import socket
import os


# Function to send a file to the client
def send_file(client_socket, filename):
    try:
        # Define the file path
        file_path = os.path.join(
            "C:/Users/devin/OneDrive/Έγγραφα/GitHub/ADKE/project3/files/",
            filename,
        )  # Change to your correct path

        if not os.path.exists(file_path):
            print(f"File {filename} not found")
            client_socket.send("ERROR: File not found".encode())
            return

        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"Preparing to send {filename}, size: {file_size} bytes")

        # Check and adjust the buffer size for the socket
        buffer_size = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        print(f"Default socket receive buffer size: {buffer_size} bytes")

        # Set a larger buffer size (e.g., 128 KB)
        new_buffer_size = 128 * 1024  # 128 KB
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, new_buffer_size)
        print(f"Setting socket receive buffer size to: {new_buffer_size} bytes")

        # Send file size
        client_socket.send(str(file_size).encode())

        # Wait for ACK from the client
        ack = client_socket.recv(1024).decode()
        if ack != "READY":
            print("Client not ready. Aborting transmission.")
            return

        # Send file in chunks
        with open(file_path, "rb") as f:
            while True:
                file_data = f.read(new_buffer_size)  # Read the file in chunks
                if not file_data:
                    break
                client_socket.sendall(file_data)  # Send each chunk

        print(f"File {filename} sent successfully")
    except BrokenPipeError:
        print(f"Client disconnected while sending {filename}")
    except Exception as e:
        print(f"Error sending file {filename}: {e}")
    finally:
        client_socket.close()


# Set up the server
def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Server listening on {ip}:{port}")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Client {client_address} connected")

            # Receive the filename from the client
            filename = client_socket.recv(1024).decode()
            print(f"Client requested: {filename}")

            send_file(client_socket, filename)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()


if __name__ == "__main__":
    server_ip = "0.0.0.0"  # Bind to all available interfaces
    server_port = 5001
    start_server(server_ip, server_port)
