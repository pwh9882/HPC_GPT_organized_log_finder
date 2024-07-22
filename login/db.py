import sqlite3
import hashlib

def create_database():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        ''', (username, email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, hashed_password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True
    else:
        return False

def delete_user(username):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM users WHERE username = ?
    ''', (username,))
    
    conn.commit()
    conn.close()
    
    return cursor.rowcount > 0

def update_user(username, new_email=None, new_password=None):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    if new_email:
        cursor.execute('''
            UPDATE users SET email = ? WHERE username = ?
        ''', (new_email, username))
        
    if new_password:
        hashed_password = hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password = ? WHERE username = ?
        ''', (hashed_password, username))
    
    conn.commit()
    conn.close()
    
    return cursor.rowcount > 0

def find_user(username):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,))
    
    user = cursor.fetchone()
    conn.close()
    
    return user
