import sqlite3
import hashlib
import os


def create_database(db_path):
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    conn = sqlite3.connect(db_path)
    conn.close()

def get_all_users(db_path):
    """Retrieves all users from the database.

    Args:
        db_path (str): The path to the SQLite database file.

    Returns:
        list: A list of tuples, where each tuple represents a user 
              and contains (id, username, password). Returns an empty list if no users are found or if there's an error.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []

def create_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_user(db_path, username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Secure Hashing
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()


def verify_user(db_path, username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user[2] == hashed_password:
        return True
    return False


# create_database("/userdatabase/userdatabase.db")
# create_table("/userdatabase/userdatabase.db")
