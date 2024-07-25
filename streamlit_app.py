from time import sleep

import streamlit as st
from login.db import create_database, register_user, authenticate_user, user_exists, get_login_cookie
from login import app as login_app

# from main_page import main_page


# def debug_auto_login():
#     st.session_state.email = "test@test.com"
#     st.session_state.password = "1234"
#     st.session_state.user_id = "test_user_id"
#     # register_user("test_user_id", "test@test.com", "1234")
#     # st.switch_page("main_page.py")
#     main_page()


def main():
    # debug_auto_login()
    pg = st.navigation(pages=[st.Page("login/app.py"), st.Page(
        "main_page.py")], position="hidden")

    print("st.session_state:", st.session_state)
    if 'user_id' not in st.session_state:
        username, hashed_password = get_login_cookie()
        if username and hashed_password:
            print("username:", username)
            print("hashed_password:", hashed_password)
            if authenticate_user(username, hashed_password, True):
                st.session_state.page = "process"
                st.session_state.user_id = username
                # sleep(0.5)
                st.switch_page("main_page.py")

    login_app.main()
    pg.run()


if __name__ == "__main__":
    create_database()
    main()
