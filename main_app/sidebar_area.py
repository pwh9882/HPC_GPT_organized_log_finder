import streamlit as st
import uuid
from login.db import insert_conversation_id_by_userid, remove_conversation_id_by_userid
import datetime


def _remove_conversation(conversation_index, conversation_id):
    del st.session_state.conversation_list[conversation_index]

    remove_conversation_id_by_userid(
        userid=st.session_state.user_id,
        conversationid=conversation_id
    )

    if st.session_state.current_conversation_id == conversation_id:
        if len(st.session_state.conversation_list) > 0:
            _load_conversation_to_main_chatbot(
                st.session_state.conversation_list[0]
            )
        else:
            st.session_state.current_conversation_id = None

    # 마지막 대화가 삭제되었을 때, 새로운 대화를 생성
    if len(st.session_state.conversation_list) == 0:
        _create_conversation()


def _create_conversation():
    conversation_id = str(uuid.uuid4())
    conversation = {
        "conversation_title": "new converstation",
        "conversation_id": conversation_id,
        "last_modified": datetime.datetime.now()
    }
    insert_conversation_id_by_userid(
        userid=st.session_state.user_id,
        conversationid=conversation_id,
        conversation_title=conversation["conversation_title"],
        date=conversation["last_modified"]

    )
    st.session_state.conversation_list.insert(0, conversation)
    # 생성된 대화를 로드
    _load_conversation_to_main_chatbot(conversation)
    return conversation


def _load_conversation_to_main_chatbot(conversation):
    chatbot = st.session_state.main_chatbot
    user_id = st.session_state.user_id
    conversation_id = conversation["conversation_id"]
    st.session_state.current_conversation_id = conversation_id
    st.session_state.current_conversation_title = conversation["conversation_title"]

    history = chatbot.get_chat_history(user_id, conversation_id).messages
    print("history loaded:\n", history)
    st.session_state.messages.clear()

    for i, message in enumerate(history):
        if i % 2 == 0:
            role = "Human"
        else:
            role = "AI"

        st.session_state.messages.append(
            {"role": role, "content": message.content})

    pass


def _conversation_tab_area(conversation_tab):
    with conversation_tab:
        # create new converstation button
        if st.button("Create New Conversation", use_container_width=True):
            _create_conversation()
            _load_conversation_to_main_chatbot(
                st.session_state.conversation_list[0]
            )
            pass

        # st.markdown("""---""")

        for conversation_index, conversation_item in enumerate(st.session_state.conversation_list):
            conversation_id = conversation_item["conversation_id"]

            # Create columns
            col1, col2 = st.columns([6, 1])

            with col1:
                if st.button(conversation_id):
                    _load_conversation_to_main_chatbot(conversation_item)
                    # st.write(f"Default functionality for {conversation_id}")

            with col2:
                if st.button("🗑️", key=f"delete_{conversation_id}"):
                    # st.write(f"Delete {conversation_id}")
                    _remove_conversation(conversation_index, conversation_id)
                    st.rerun()
            pass
    pass


def _search_tab_area(search_tab):
    with search_tab:
        pass
    pass


def sidebar_area():
    with st.sidebar:
        conversation_tab, search_tab = st.tabs(["Conversation", "Search"])

        _conversation_tab_area(conversation_tab)
        _search_tab_area(search_tab)

    pass


if __name__ == "__main__":
    sidebar_area()
