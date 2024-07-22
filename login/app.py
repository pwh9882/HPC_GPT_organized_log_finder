import streamlit as st
from db import create_database, register_user, authenticate_user, delete_user, update_user, find_user

def main():
    create_database()
    
    st.title("User Authentication System")

    menu = ["Home", "Login", "SignUp", "Delete", "Update", "Find"]
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
                
    elif choice == "Delete":
        st.subheader("Delete Account")

        username = st.text_input("Username to delete")
        if st.button("Delete"):
            if delete_user(username):
                st.success(f"User {username} deleted successfully")
            else:
                st.warning("User not found")

    elif choice == "Update":
        st.subheader("Update Account Information")

        username = st.text_input("Username to update")
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type='password')

        if st.button("Update"):
            if update_user(username, new_email, new_password):
                st.success(f"User {username} updated successfully")
            else:
                st.warning("User not found or no changes made")
    
    elif choice == "Find":
        st.subheader("Find User")

        username = st.text_input("Username to find")
        if st.button("Find"):
            user = find_user(username)
            if user:
                st.success(f"User found: {user}")
            else:
                st.warning("User not found")

if __name__ == '__main__':
    main()
