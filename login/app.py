import streamlit as st
from db import create_database, register_user, authenticate_user

def main():
    # 애플리케이션 시작 시 데이터베이스 생성
    create_database()
    
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
