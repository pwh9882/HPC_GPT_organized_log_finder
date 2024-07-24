from time import sleep

import streamlit as st
from login.db import create_database, register_user, authenticate_user, user_exists
from login import app as login_app


def main():
    pg = st.navigation(pages=[st.Page("login/app.py"), st.Page(
        "main_app.py")], position="hidden")
    pg.run()
    login_app.main()


if __name__ == "__main__":
    create_database()
    main()
