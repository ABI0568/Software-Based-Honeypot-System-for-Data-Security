# Software-Based Honeypot System for Data Security

## Abstract
This project presents the design and implementation of a software-based honeypot system aimed at attracting potential attackers and studying their behavior in a controlled environment. The system simulates vulnerable services and fake resources that appear legitimate to attackers, thereby diverting them away from real production systems. Any unauthorized access attempts, login activities, and suspicious actions are captured and logged without exposing actual sensitive data.

Developed as a flexible software application suitable for virtualized environments, this honeypot provides proactive data security. It records critical attack information (IP addresses, timestamps, attempted credentials) and stores it securely. This collected data is then analyzed to identify common attack techniques and intrusion trends. Real-time alerts and analytical reports are generated to assist administrators in improving overall security policies through early attack detection and improved incident response.

## Features
- **Early Attack Detection**: Simulates vulnerable services (raw TCP on port `2222`) to divert attacks from real infrastructure.
- **Detailed Logging**: Records capturing IP addresses, timestamps, and attempted credentials.
- **Real-Time Alerts**: Prints immediate security alerts to the console upon intrusion attempts.
- **Data Security**: Stores attack data securely in a local SQLite database (`honeypot_logs.db`) and a log file (`honeypot_activity.log`).
- **Trend Analysis & Reporting**: Includes an analysis tool (`generate_report.py`) to parse the database for common attack techniques, trends, and top malicious IPs.

## Files Included
- `honeypot.py`: The main honeypot server script.
- `test_client.py`: A simple client script to verify the honeypot is capturing data correctly.
- `generate_report.py`: An administrative script to generate threat intelligence reports based on captured data.

## How to Run the Server

1. Open your terminal or Command Prompt.
2. Navigate to the project folder (`c:\honeypot`).
3. Start the honeypot server:
   ```powershell
   python honeypot.py
   ```
4. The server will display a banner and start listening on port 2222. Keep this terminal window open to keep the server running.

## How to Test the Honeypot

Because this is a raw TCP server and not a cryptographically complete SSH server, standard `ssh` commands will fail. Instead, use the included test script or a plain text client like Telnet/Netcat.

### Using the Test Script
1. Ensure `honeypot.py` is currently running in one terminal.
2. Open a **new, separate terminal window**.
3. Run the test script:
   ```powershell
   python test_client.py
   ```
4. The script will automatically connect, see the server's fake prompts, and send a fake username (`admin`) and password (`hacker123`).
5. After running it, check the `honeypot_activity.log` file and the `honeypot_logs.db` database to see the recorded "attack"!

### Using Telnet (Optional)
If you have Telnet enabled on Windows, you can also interact with the honeypot manually:
```powershell
telnet localhost 2222
```
