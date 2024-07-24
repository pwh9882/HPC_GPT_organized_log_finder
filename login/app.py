from time import sleep

import streamlit as st
from login.db import create_database, register_user, authenticate_user, user_exists


def main():
    # pg = st.navigation(pages=[st.Page("app.py"), st.Page("pages/streamlit_app.py")], position="hidden")
    # pg.run()

    if 'page' not in st.session_state:
        st.session_state.page = 'login'

    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'signup':
        signup_page()
    # elif st.session_state.page == 'forgot_password':
    #     forgot_password_page()


def login_page():
    st.title("GOLF")
    st.markdown("---")

    st.text_input("이메일", key="login_username")
    st.text_input("비밀번호", type='password', key="login_password")

    if st.button("로그인"):
        username = st.session_state.login_username
        password = st.session_state.login_password
        if authenticate_user(username, password):
            st.success(f"Welcome {username}")

            st.session_state.page = "process"
            st.session_state.user_id = username
            sleep(0.5)
            st.switch_page("main_page.py")
        else:
            st.warning("Incorrect Username/Password")

    # if st.button("비밀번호를 잊으셨나요?"):
    #     st.session_state.page = 'forgot_password'
    #     st.rerun()

    st.markdown("---")
    if st.button("계정이 없으신가요? 가입하기"):
        st.session_state.page = 'signup'
        st.rerun()


def signup_page():
    st.title("GOLF")

    st.markdown("---")

    new_email = st.text_input("이메일")
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
        st.rerun()


# def forgot_password_page():
#     st.title("비밀번호 찾기")

#     email = st.text_input("이메일 주소를 입력하세요")

#     if st.button("비밀번호 재설정 링크 보내기"):
#         if user_exists(email):
#             if send_reset_email(email):
#                 st.success("비밀번호 재설정 링크가 이메일로 전송되었습니다.")
#             else:
#                 st.error("이메일 전송에 실패했습니다. 나중에 다시 시도해주세요.")
#         else:
#             st.error("등록되지 않은 이메일 주소입니다.")

#     if st.button("로그인 페이지로 돌아가기"):
#         st.session_state.page = 'login'
#         st.rerun()


# if __name__ == "__main__":
#     create_database()
#     main()

# create_database()
# main()
