import streamlit as st

from RAG_chatbot.RAGChatbot import RAGChatbot
from areas.main_area import main_area
from areas.sidebar_area import sidebar_area
from summerizer.summerizer import SQLSummaryChatBot
from login.db import get_all_conversation_id_by_userid
from RAG_chatbot.embedding.SummaryEmbedder import SummaryEmbedder


def _load_main_chatbot():
    if "main_chatbot" not in st.session_state:
        st.session_state.main_chatbot = SQLSummaryChatBot()
    if "conversation_chatbot" not in st.session_state:
        st.session_state.conversation_chatbot = RAGChatbot(
            st.session_state.user_id)
    if "summary_embedder" not in st.session_state:
        st.session_state.summary_embedder = SummaryEmbedder()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_messages" not in st.session_state:
        st.session_state.conversation_messages = []
    if "current_conversation_title" not in st.session_state:
        st.session_state.current_conversation_title = "임시 대화창"
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = "임시 대화창"
    if "conversation_link_count" not in st.session_state:
        # search tab에서 AI가 찾아준 대화 버튼에 부여할 버튼 키를 위한 카운트
        st.session_state.conversation_link_count = 0


def _load_user_data_from_db():
    userid = st.session_state.user_id
    st.session_state.conversation_list = get_all_conversation_id_by_userid(
        userid
    )
    # print(st.session_state.conversation_list)


def main_page():
    if "user_id" not in st.session_state:
        st.switch_page("login/app.py")
    _load_user_data_from_db()
    _load_main_chatbot()

    sidebar_area()
    main_area()
    pass


# if __name__ == "__main__":
#     main_page()
main_page()
