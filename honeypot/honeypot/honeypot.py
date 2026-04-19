import socket               # Used for network communication
import threading            # Used to handle multiple attackers simultaneously
import sqlite3              # Used for database storage
import logging              # Used to log attacker activities
from datetime import datetime  # Used to record date and time
import sys                  # Used for system-level operations

# =========================
# GLOBAL CONFIGURATIONS
# =========================

HOST = "0.0.0.0"            # Listen on all available interfaces
PORT = 2222                 # Fake service port (acts like SSH)
import os

# Get directory of current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_NAME = os.path.join(SCRIPT_DIR, "honeypot_logs.db")
LOG_FILE = os.path.join(SCRIPT_DIR, "honeypot_activity.log")

# =========================
# LOGGING CONFIGURATION
# =========================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# DATABASE INITIALIZATION
# =========================

def initialize_database():
    """
    ----------------------------------------------------------------
    FUNCTION NAME : initialize_database
    ----------------------------------------------------------------
    PURPOSE:
    This function initializes the SQLite database used to store
    attacker details captured by the honeypot system.

    If the database or table does not exist, it is created.
    ----------------------------------------------------------------
    """
    try:
        # Establish connection to SQLite database
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()

        # SQL command to create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                username TEXT,
                password TEXT,
                timestamp TEXT,
                status TEXT
            )
        """)
        connection.commit()
        connection.close()
    except Exception as e:
        print("Database initialization failed:", e)
        sys.exit(1)

# =========================
# ATTACK LOGGING FUNCTION
# =========================

def log_attack(ip_address, username, password):
    """
    ----------------------------------------------------------------
    FUNCTION NAME : log_attack
    ----------------------------------------------------------------
    PURPOSE:
    This function logs attacker details into both:
    1. Log file (for quick review)
    2. SQLite database (for analysis and reporting)
    ----------------------------------------------------------------
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate a real-time console alert
    print(f"\n[!] SECURITY ALERT: Unauthorized access attempt detected!")
    print(f"    -> Source IP : {ip_address}")
    print(f"    -> Timestamp : {timestamp}")
    print(f"    -> Identity  : {username}\n")

    # Write attack details to log file
    logging.info(
        f"Attack Detected | IP: {ip_address} | "
        f"Username: {username} | Password: {password}"
    )

    try:
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO attack_logs
            (ip_address, username, password, timestamp, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ip_address,
            username,
            password,
            timestamp,
            "FAILED"
        ))
        connection.commit()
        connection.close()

    except Exception as e:
        logging.error(f"Database logging error: {e}")

# =========================
# CLIENT HANDLING FUNCTION
# =========================

def handle_attacker(client_socket, client_address):
    """
    ----------------------------------------------------------------
    FUNCTION NAME : handle_attacker
    ----------------------------------------------------------------
    PURPOSE:
    This function handles a single attacker connection.
    It simulates a login prompt and captures credentials.
    ----------------------------------------------------------------
    """
    ip_address = client_address[0]
    client_file = None

    try:
        client_file = client_socket.makefile('r', encoding='utf-8', errors='replace')
        
        # Send fake server banner and username prompt
        client_socket.sendall(b"Welcome to Secure Remote Server v1.0\n")
        client_socket.sendall(b"Username: ")

        # Receive username
        username_line = client_file.readline()
        if not username_line:
            username = "<empty_or_binary>"
            password = "<empty_or_binary>"
        else:
            username = username_line.strip() or "<empty_or_binary>"
            
            # Send fake password prompt
            client_socket.sendall(b"Password: ")
            
            # Receive password
            password_line = client_file.readline()
            password = password_line.strip() if password_line else "<empty_or_binary>"

        # Log attack attempt
        log_attack(ip_address, username, password)

        # Send fake authentication failure message
        client_socket.sendall(b"Authentication failed. Connection terminated.\n")

    except Exception as e:
        logging.error(f"Error handling attacker {ip_address}: {e}")

    finally:
        # Close attacker connection
        if client_file:
            client_file.close()
        client_socket.close()

# =========================
# HONEYPOT SERVER FUNCTION
# =========================

def start_honeypot_server():
    """
    ----------------------------------------------------------------
    FUNCTION NAME : start_honeypot_server
    ----------------------------------------------------------------
    PURPOSE:
    This function starts the honeypot server and continuously
    listens for incoming connections from attackers.
    ----------------------------------------------------------------
    """
    initialize_database()

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Added socket option to allow port reuse right after the script closes
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

        print("=" * 60)
        print(" SOFTWARE-BASED HONEYPOT SYSTEM RUNNING ")
        print(f" Listening on port {PORT}")
        print("=" * 60)

    except Exception as e:
        print("Failed to start honeypot server:", e)
        sys.exit(1)

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            attacker_thread = threading.Thread(
                target=handle_attacker,
                args=(client_socket, client_address)
            )
            attacker_thread.start()

        except KeyboardInterrupt:
            print("\nHoneypot server stopped manually.")
            server_socket.close()
            sys.exit(0)

        except Exception as e:
            logging.error(f"Server error: {e}")

# =========================
# MAIN FUNCTION
# =========================

if __name__ == "__main__":
    """
    ----------------------------------------------------------------
    MAIN EXECUTION BLOCK
    ----------------------------------------------------------------
    This block ensures that the honeypot server starts only when
    the script is executed directly.
    ----------------------------------------------------------------
    """
    start_honeypot_server()
