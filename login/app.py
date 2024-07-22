import sqlite3
import hashlib
import streamlit as st

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

def main():
    # Streamlit 애플리케이션 UI 설정
    st.title("User Authentication System")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            if authenticate_user(username, password):
                st.success(f"Welcome {username}")
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create New Account")

        new_user = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type='password')

        if st.button("SignUp"):
            if register_user(new_user, new_email, new_password):
                st.success("You have successfully created an account")
            else:
                st.warning("Username or Email already exists")

if __name__ == '__main__':
    main()
