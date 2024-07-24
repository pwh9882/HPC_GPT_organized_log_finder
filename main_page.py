import streamlit as st
from main_app.main_area import main_area
from main_app.sidebar_area import sidebar_area
from summerizer.summerizer import SQLSummaryChatBot
from login.db import get_all_conversation_id_by_userid
from RAG_chatbot.embedding.SummaryEmbedder import SummaryEmbedder


def _load_main_chatbot():
    if "main_chatbot" not in st.session_state:
        st.session_state.main_chatbot = SQLSummaryChatBot()
    if "summary_embedder" not in st.session_state:
        st.session_state.summary_embedder = SummaryEmbedder()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_conversation_title" not in st.session_state:
        st.session_state.current_conversation_title = "임시 대화창"
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = "임시 대화창"


def _load_user_data_from_db():
    userid = st.session_state.user_id
    st.session_state.conversation_list = get_all_conversation_id_by_userid(
        userid
    )
    # print(st.session_state.conversation_list)


def main_page():
    _load_user_data_from_db()
    _load_main_chatbot()

    sidebar_area()
    main_area()
    pass


if __name__ == "__main__":
    main_page()
