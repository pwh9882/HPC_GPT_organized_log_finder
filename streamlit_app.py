import streamlit as st
from streamlit_extras.grid import grid
import copy

from summerizer.summerizer import SQLSummaryChatBot


if "main_chatbot" not in st.session_state:
    st.session_state.main_chatbot = SQLSummaryChatBot()


def load_conversation(conversation_id):
    chatbot = st.session_state.main_chatbot

    user_id = st.session_state.user_id
    st.session_state.conversation_id = conversation_id

    history = chatbot.get_chat_history(user_id, conversation_id).messages
    st.session_state.messages.clear()

    for i, message in enumerate(history):
        if i % 2 == 0:
            role = "Human"
        else:
            role = "AI"

        st.session_state.messages.append({"role": role, "content": message.content})


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = "user1"

if "conversation_id" not in st.session_state:
    load_conversation("conversation1")


def draw_session_title():
    global title_placeholder
    title_placeholder.title(st.session_state.conversation_id)


title_placeholder = st.empty()
draw_session_title()

with st.sidebar:
    st.button("Create Session", use_container_width=True)

    with st.container(height=300, border=True):
        def on_session_button_clicked(id):
            load_conversation(id)
            draw_session_title()

        for i in range(1, 11):
            if st.button("session" + str(i), use_container_width=True):
                on_session_button_clicked("conversation" + str(i))
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
if prompt := st.chat_input("Message"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


