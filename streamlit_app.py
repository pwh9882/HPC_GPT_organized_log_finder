import streamlit as st
from streamlit_extras.grid import grid
import copy
import uuid

from summerizer.summerizer import SQLSummaryChatBot


if "main_chatbot" not in st.session_state:
    st.session_state.main_chatbot = SQLSummaryChatBot()


def create_conversation():
    conversation_id = str(uuid.uuid4())
    session = {"session_name": "new session", "conversation_id": conversation_id}
    st.session_state.session_list.insert(0, session)
    return session


def load_conversation(session):
    chatbot = st.session_state.main_chatbot

    user_id = st.session_state.user_id
    st.session_state.session = session
    conversation_id = session["conversation_id"]

    history = chatbot.get_chat_history(user_id, conversation_id).messages
    st.session_state.messages.clear()

    for i, message in enumerate(history):
        if i % 2 == 0:
            role = "Human"
        else:
            role = "AI"

        st.session_state.messages.append({"role": role, "content": message.content})

def get_session_id_by_session_name(session_name):
    for i, session in enumerate(st.session_state.session_list):
        if session["session_name"] == session_name:
            return i

def remove_conversation(session_id):
    flag = False
    if st.session_state.session == st.session_state.session_list[session_id]:
        flag = True

    del st.session_state.session_list[session_id]

    if flag:
        session = create_conversation()
        load_conversation(session)

def rename_conversation(session_id, new_session_name):
    if st.session_state.session_list[session_id] == st.session_state.session:
        st.session_state.session["session_name"] = new_session_name
    st.session_state.session_list[session_id]["session_name"] = new_session_name


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_list" not in st.session_state:
    st.session_state.session_list = []
    for i in range(10):
        st.session_state.session_list.append({"session_name": f"session{i+1}", "conversation_id": f"conversation{i+1}"})

if "session" not in st.session_state:
    load_conversation(st.session_state.session_list[0])


def draw_session_title():
    global title_placeholder
    title_placeholder.title(st.session_state.session["session_name"])


title_placeholder = st.empty()
draw_session_title()


def draw_session_button(key, on_click):
    for i, session in enumerate(st.session_state.session_list):
        if st.button(session["session_name"], use_container_width=True, key=key + str(i)):
            on_click(i)


with st.sidebar:
    session_tab, search_tab = st.tabs(["Session", "Search"])

    with session_tab:
        if st.button("Create Session", use_container_width=True):
            session = create_conversation()
            load_conversation(session)
            draw_session_title()

        if st.button("Remove Session", use_container_width=True):
            @st.experimental_dialog("Remove Session", width="large")
            def remove_dialog():
                st.write("Click session which you want to remove")
                with st.container(height=600, border=True):
                    def on_session_button_clicked(i):
                        remove_conversation(i)
                        draw_session_title()
                        st.rerun()

                    draw_session_button("e362a88b-e99c-4312-ac94-5e31dda0e042", on_session_button_clicked)

            remove_dialog()

        if st.button("Rename Session", use_container_width=True):
            st.session_state.choose_session_id = -1

            @st.experimental_dialog("Rename Session", width="large")
            def rename_dialog():
                if st.session_state.choose_session_id == -1:
                    st.write("Click session which you want to rename")
                    with st.container(height=600, border=True):
                        key = "4a0ec9a9-1415-4358-ab9d-262430367d8c"
                        for i, session in enumerate(st.session_state.session_list):
                            if st.button(session["session_name"], use_container_width=True, key=key + str(i)):
                                draw_session_title()
                                st.session_state.choose_session_id = i
                else:
                    new_session_name = st.text_input("Write new name",
                                                     st.session_state.session_list[st.session_state.choose_session_id]["session_name"])
                    if st.button("Rename", use_container_width=True):
                        rename_conversation(st.session_state.choose_session_id, new_session_name)

            rename_dialog()

        with st.container(height=600, border=True):
            def on_session_button_clicked(i):
                load_conversation(st.session_state.session_list[i])
                draw_session_title()

            draw_session_button("98296fec-185a-472c-9015-c2e5953cce43", on_session_button_clicked)

    with search_tab:
        with st.container(height=600, border=True):
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
    chatbot = st.session_state.main_chatbot

    user_id = st.session_state.user_id
    conversation_id = st.session_state.session["conversation_id"]

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "Human", "content": prompt})

    response = chatbot.invoke_chain(prompt, user_id, conversation_id)
    # Display assistant response in chat message container
    with st.chat_message("AI"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "AI", "content": response})
