import sqlite3
from collections import Counter
import os
import sys

DATABASE_NAME = "honeypot_logs.db"

def generate_security_report():
    """
    ----------------------------------------------------------------
    FUNCTION NAME : generate_security_report
    ----------------------------------------------------------------
    PURPOSE:
    This function connects to the honeypot SQLite database and
    analyzes the collected data to identify common attack techniques
    and intrusion trends. It generates a summary report to assist
    administrators in improving overall security policies.
    ----------------------------------------------------------------
    """
    if not os.path.exists(DATABASE_NAME):
        print(f"[-] Database {DATABASE_NAME} not found. No data to analyze.")
        sys.exit(1)

    try:
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        
        # Load all attack logs
        cursor.execute("SELECT ip_address, username, password, timestamp FROM attack_logs")
        rows = cursor.fetchall()
        connection.close()
        
        if not rows:
            print("[i] The database is empty. No attacks logged yet.")
            return

        print("==========================================================")
        print("          HONEYPOT SECURITY INTELLIGENCE REPORT           ")
        print("==========================================================\n")

        print(f"[*] Total Intrusion Attempts Logged: {len(rows)}\n")

        # Extract columns
        ips = [row[0] for row in rows]
        usernames = [row[1] for row in rows]
        passwords = [row[2] for row in rows]
        dates = [row[3][:10] for row in rows if row[3]] # Extract YYYY-MM-DD

        # 1. Top Attacking IP Addresses
        print("[*] Top 5 Malicious IP Addresses:")
        for ip, count in Counter(ips).most_common(5):
            print(f"    - {ip}: {count} attempts")
        print()

        # 2. Most Targeted Usernames
        print("[*] Top 5 Targeted Usernames (Attack Techniques):")
        for user, count in Counter(usernames).most_common(5):
            print(f"    - {user}: {count} attempts")
        print()

        # 3. Most Common Passwords Attempted (Dictionary Attacks)
        print("[*] Top 5 Attempted Passwords (Intrusion Trends):")
        for pwd, count in Counter(passwords).most_common(5):
            print(f"    - {pwd}: {count} attempts")
        print()

        # 4. Activity Over Time (Basic Trend)
        print("[*] Attack Frequency by Date:")
        date_counts = Counter(dates)
        for date in sorted(date_counts.keys()):
            print(f"    - {date}: {date_counts[date]} attempts")

        print("\n==========================================================")
        print("  REPORT GENERATED SUCCESSFULLY TO ASSIST ADMINISTRATORS  ")
        print("==========================================================")

    except Exception as e:
        print(f"[-] Error generating report: {e}")

if __name__ == "__main__":
    generate_security_report()
