# Nexus Campus - Student Database

A beautiful, fully functional Student Database built using Python (Flask) and SQLite. 

## Features
- **Student Management:** Easily add new students, view the entire roster, update existing records, and delete students securely.
- **Modern User Interface:** Features a stunning "glassmorphism" aesthetic, sleek animations, and responsive interactions right in your browser.
- **Data Persistence:** Automatically manages a local SQLite database inside this folder (`students.db`) so your records are saved permanently between sessions.

---

## 🚀 How to Run the Code

To start using the Student Database, open your terminal (Command Prompt or PowerShell) and ensure you are in the project's folder:
`cd "c:\new projects\login page"`

**Step 1: Install Dependencies**
You only need to do this once. Ensure you have Python installed, then run:

```bash
pip install -r requirements.txt
```
*(This installs the required Flask and Flask-SQLAlchemy packages)*

**Step 2: Start the Web Server**
To launch the backend server, run this command:

```bash
python app.py
```

**Step 3: Open in Browser**
Once the server starts up, you will see a message in your terminal saying `* Running on http://127.0.0.1:5000`. 
Leave the terminal open and running. Open your web browser (Chrome, Edge, Firefox, etc.) and navigate to:

👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

**Step 4: Stopping the Application**
When you are completely finished using the website, return to the open terminal window and press **`Ctrl + C`** on your keyboard to stop the server gracefully.
