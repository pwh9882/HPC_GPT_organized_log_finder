import streamlit as st
from streamlit_extras.grid import grid
import copy

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = 0


def draw_session_title():
    global title_placeholder
    title_placeholder.title("Session" + str(st.session_state.session_id))


title_placeholder = st.empty()
draw_session_title()

with st.sidebar:
    st.button("Create Session", use_container_width=True)

    with st.container(height=300, border=True):
        def on_session_button_clicked(id):
            st.session_state.session_id = id
            draw_session_title()


        for i in range(1, 11):
            if st.button("session" + str(i), use_container_width=True):
                on_session_button_clicked(i)
            # st.page_link(page="streamlit_app.py", label="session" + str(i))

    with st.container(height=300, border=True):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    st.chat_input("Session search")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
