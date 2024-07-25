import sqlite3
import hashlib
from datetime import datetime


def create_database():
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

    # conversation 테이블을 생성합니다.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation (
            userid TEXT NOT NULL,
            conversationid TEXT NOT NULL,
            conversation_title TEXT NOT NULL,
            last_modified TEXT NOT NULL,
            PRIMARY KEY (userid, conversationid)
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


def authenticate_user(email, password):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute('''
        SELECT * FROM users WHERE email = ? AND password = ?
    ''', (email, hashed_password))

    user = cursor.fetchone()
    conn.close()

    return user is not None


def user_exists(email):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE email = ?
    ''', (email,))

    user = cursor.fetchone()
    conn.close()

    return user is not None


def delete_user(email):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM users WHERE email = ?
    ''', (email,))

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

# Conversation DB functions


def insert_conversation_id_by_userid(userid, conversationid, conversation_title, date):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    try:
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO conversation (userid, conversationid, conversation_title, last_modified)
            VALUES (?, ?, ?, ?)
        ''', (userid, conversationid, conversation_title, formatted_date))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True


def remove_conversation_id_by_userid(userid, conversationid):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM conversation WHERE userid = ? AND conversationid = ?
    ''', (userid, conversationid))

    conn.commit()
    conn.close()

    return cursor.rowcount > 0


def get_all_conversation_id_by_userid(userid):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT conversationid, conversation_title, last_modified FROM conversation WHERE userid = ?
        ORDER BY last_modified DESC
    ''', (userid,))

    conversations = cursor.fetchall()
    conn.close()

    # last_modified를 Python의 datetime 객체로 변환
    result = [
        {
            'conversation_id': cid,
            'conversation_title': title,
            'last_modified': datetime.strptime(last_modified, '%Y-%m-%d %H:%M:%S')
        }
        for cid, title, last_modified in conversations
    ]

    return result


def update_conversation_by_conversation_id(conversationid, conversation_title):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

    date = datetime.now()

    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE conversation SET conversation_title = ?, last_modified = ? WHERE conversationid = ?
    ''', (conversation_title, formatted_date, conversationid))

    conn.commit()
    conn.close()

    return cursor.rowcount > 0


if __name__ == "__main__":
    create_database()
