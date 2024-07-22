import os
import django
from myapp.db import create_database, register_user, authenticate_user

# Django 설정 파일을 사용하도록 환경 변수 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

import streamlit as st

def main():
    # 페이지 상태를 세션 상태로 관리
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'signup':
        signup_page()

def login_page():
    st.title("GOLF")

    st.markdown("---")

    st.text_input("전화번호, 사용자 이름 또는 이메일", key="login_username")
    st.text_input("비밀번호", type='password', key="login_password")
    
    if st.button("로그인"):
        username = st.session_state.login_username
        password = st.session_state.login_password
        if authenticate_user(username, password):
            st.success(f"Welcome {username}")
        else:
            st.warning("Incorrect Username/Password")

    st.markdown("비밀번호를 잊으셨나요?", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("계정이 없으신가요? 가입하기"):
        st.session_state.page = 'signup'
        st.experimental_rerun()

def signup_page():
    st.title("GOLF")

    st.markdown("---")

    new_email = st.text_input("휴대폰 번호 또는 이메일 주소")
    name = st.text_input("성명")
    new_user = st.text_input("사용자 이름")
    new_password = st.text_input("비밀번호", type='password')

    if st.button("가입"):
        if register_user(new_user, new_email, new_password):
            st.success("You have successfully created an account")
        else:
            st.warning("Username or Email already exists")

    if st.button("계정이 있으신가요? 로그인"):
        st.session_state.page = 'login'
        st.experimental_rerun()

if __name__ == "__main__":
    create_database()
    main()
