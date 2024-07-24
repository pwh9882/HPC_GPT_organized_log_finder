import sqlite3

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

if __name__ == "__main__":
    create_database()
