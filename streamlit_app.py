from time import sleep

import streamlit as st
from login.db import create_database, register_user, authenticate_user, user_exists
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
    pg.run()

    login_app.main()


if __name__ == "__main__":
    create_database()
    main()
