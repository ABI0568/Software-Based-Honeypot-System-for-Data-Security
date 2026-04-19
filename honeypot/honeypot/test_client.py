import socket
import time

def recv_until(sock, prompt):
    buffer = b""
    while prompt not in buffer:
        chunk = sock.recv(1024)
        if not chunk:
            break
        buffer += chunk
    return buffer.decode('utf-8', errors='replace')

# Connect to the honeypot
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 2222))

# Receive the Welcome Banner and Username prompt
print(recv_until(client, b"Username: "), end="", flush=True)
time.sleep(1) # Add a small delay to simulate human interaction

# Send fake username
print("admin", flush=True) # Print it so the user sees the input
client.sendall(b"admin\n")

print(recv_until(client, b"Password: "), end="", flush=True)
time.sleep(1)

# Send fake password
print("hacker123", flush=True)
client.sendall(b"hacker123\n")

print(recv_until(client, b"terminated.\n"), end="", flush=True)

client.close()
