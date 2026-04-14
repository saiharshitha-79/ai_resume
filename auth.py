import sqlite3
import bcrypt
import datetime

DB_NAME = "users.db"

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    # History table for tracking scores
    c.execute('''
        CREATE TABLE IF NOT EXISTS history_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            target_role TEXT NOT NULL,
            score REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    """Registers a new user with a hashed password."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Hash the password using bcrypt
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        return True, "Registration successful! Please login."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose a different one."
    finally:
        conn.close()

def login_user(username, password):
    """Verifies a user's password against the stored hash."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()

    if result:
        stored_hashed_pw = result[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_pw):
            return True, "Login successful!"
    return False, "Invalid username or password."

def save_score(username, target_role, score):
    """Saves an ATS score analysis entry to the user's history."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO history_logs (username, target_role, score) 
        VALUES (?, ?, ?)
    ''', (username, target_role, float(score)))
    conn.commit()
    conn.close()

def get_user_history(username):
    """Retrieves all previous ATS scores for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT target_role, score, timestamp 
        FROM history_logs 
        WHERE username = ? 
        ORDER BY timestamp ASC
    ''', (username,))
    
    # Format into list of dicts
    results = [{"target_role": row[0], "score": row[1], "timestamp": row[2]} for row in c.fetchall()]
    conn.close()
    return results

# Initialize the db on import
init_db()
