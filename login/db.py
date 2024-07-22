import sqlite3
import hashlib

def create_database():
    # 데이터베이스 파일을 연결하거나 생성합니다.
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    
    # users 테이블을 생성합니다.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # 변경사항을 저장하고 연결을 종료합니다.
    conn.commit()
    conn.close()

def hash_password(password):
    # 비밀번호를 해시화합니다.
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    # 데이터베이스에 새로운 사용자 정보를 추가합니다.
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
    # 사용자 인증을 처리합니다.
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
