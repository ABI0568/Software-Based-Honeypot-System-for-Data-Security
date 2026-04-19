# Project Definition & Architecture Guide

This document provides a comprehensive breakdown of the Honeypot-integrated Student Database project. It details the purpose, process, and logic of each script within the project and explains how the system operates as a whole.

## 1. High-Level Process Overview

This project is a two-part system:
1. **The Web Application (`login_page/`)**: A Flask-based Student Database that allows users to register, log in, view, add, edit, and delete student records.
2. **The Security Honeypot (`honeypot/`)**: A dual-purpose security module that operates as a standalone fake server (listening on port 2222) and as a security backend for the web application.

### The Core Process (How the Honeypot intercepts attackers)
When a user attempts to log into the web application via `login_page/app.py`:
- **Legitimate Users:** If the credentials are correct, they are authenticated normally. They are granted access to the **Real Database** (`instance/students.db`) where actual student records are stored.
- **Attackers/Unauthenticated Users:** If the user enters incorrect credentials, instead of simply denying access, the system traps them:
  1. The system invokes `log_attack(ip, username, password)` from the `honeypot` module, which silently records the attackers' IP, target username, and password attempt into `honeypot/honeypot_logs.db`.
  2. The system deliberately fakes a successful login by modifying the user's session state (`session['is_hacker'] = True`).
  3. The attacker is seamlessly redirected to the application but is secretly bound to a **Fake Database** (`honeypot/fake_database.db`). Any actions they perform (viewing data, adding, or deleting files) only affect the fake data, protecting the real data while the attacker wastes their time and reveals their methodology.

---

## 2. Directory & File Breakdown

### A. The Web Application (`c:\honeypot\login_page\`)

#### 1. `app.py`
This is the core server for the web interface.
- **Process:** It initializes the Flask application and an SQLAlchemy object mapped to two different databases simultaneously using Flask-SQLAlchemy binds (Real DB vs. Fake DB).
- **Key Logic:**
  - **Models:** `User` (for auth), `RealStudent` (real internal data), `FakeStudent` (honeypot schema).
  - **Dynamic Routing (`get_student_model`):** A helper function that checks `session.get('is_hacker')` on every request to dynamically swap out the database the user queries.
  - **`/login` Route:** The pivotal logic flow. Verifies password hashes. Upon failure, it logs the IP, sets the hacker flag, but still flashes "Successfully logged in!" to trick the attacker.
  - **CRUD Operations (`/add`, `/edit`, `/delete`):** Uses standard SQLAlchemy logic to manage records, perfectly mirroring normal functionality whether the user is legitimate or trapped in the honeypot.

#### 2. `seed_db.py`
The database population script.
- **Process:** Run manually before starting the app to ensure both databases have tables and initial test data.
- **Key Logic:** Drops any existing tables, creates an admin user, populates the `RealStudent` table with 10 actual students, and populates the `FakeStudent` table with 20 dummy accounts.

#### 3. `requirements.txt`
- **Process:** Contains backend python dependencies required to run the web stack (`Flask`, `Flask-SQLAlchemy`, and inherently `Werkzeug` for password hashing).

#### 4. `templates/` (HTML Files)
- **`base.html`**: The unified layout featuring a modern glassmorphism UI. Includes navigation routing and flash message rendering.
- **`index.html`**: The main dashboard that iterates over the `students` list to populate a table of records.
- **`login.html` & `register.html`**: User authentication forms.
- **`add_edit.html`**: Reusable form design for inserting or modifying student entries.

### B. The Security Honeypot (`c:\honeypot\honeypot\`)

#### 1. `honeypot.py`
The main security backend engine. Operates in two ways: as an imported module and as a standalone server.
- **Process (Standalone):** When run directly, it opens a raw TCP socket on Port 2222 (similar to SSH). It listens for connections and mimics a raw server interface (`Welcome to Secure Remote Server v1.0`).
- **Process (Module):** It provides the `log_attack` function to `app.py`.
- **Key Logic:**
  - `initialize_database()`: Ensures the `honeypot_logs.db` exists with an `attack_logs` table.
  - `log_attack()`: Writes intelligence data (IP, Username, Password, Time) to both an SQLite database and a flat text file (`honeypot_activity.log`).
  - Contains threading to handle multiple simultaneous brute-force attackers safely on Port 2222 without hanging the server processing them.

#### 2. `generate_report.py`
A data analytics script for security administrators.
- **Process:** Connects to `honeypot_logs.db` and builds a "Security Intelligence Report".
- **Key Logic:** Reads the logs into memory, utilizes Python's `collections.Counter` to identify trend lines:
  - Top 5 Malicious IP Addresses
  - Most Targeted Usernames
  - Most Common Initial Passwords (indicating dictionary attack sources)
  - Frequency of attacks plotted across calendar dates.

#### 3. `test_client.py`
A diagnostic script designed to mimic an attacker.
- **Process:** Specifically connects to `127.0.0.1:2222` to verify the standalone honeypot.
- **Key Logic:** Programmatically waits for the `Username:` and `Password:` prompts via raw socket buffer parsing, and auto-injects standard bad actor credentials (`admin`/`hacker123`).

#### 4. The Data Stores
- **`honeypot_logs.db`**: SQLite database recording the metadata of attackers (IPs and credentials).
- **`honeypot_activity.log`**: A raw text append-only logger format of the attacks.
- **`fake_database.db`**: The SQLite database the Flask app redirects attackers toward.

---

## 3. Summary of Interactions

The genius of this project is the seamless handoff between the web application and the honeypot:

1. A bot or attacker scrapes `http://your-site/login`.
2. They launch a dictionary attack using standard passwords.
3. Because the passwords fail, `app.py` flags the user context as hostile (`session['is_hacker'] = True`).
4. `app.py` passes the username, IP, and password used to `honeypot.py` which records this in `honeypot_logs.db`.
5. The attacker successfully logs in (so they think) and begins trying to drop tables, exfiltrate user data, or inject XSS into user records within the dashboard.
6. The `get_student_model()` silently masks the real SQL bindings with `FakeStudent`, capturing their interactions inside `fake_database.db`.
7. Administrators can periodically run `generate_report.py` to harvest threat intelligence (such as IP addresses to block at the firewall) without putting real system data at risk.
