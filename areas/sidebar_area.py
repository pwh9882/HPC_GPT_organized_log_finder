import streamlit as st
import uuid
from login.db import insert_conversation_id_by_userid, remove_conversation_id_by_userid, delete_user
import datetime
from time import sleep


def _remove_conversation(conversation_id):

    if st.session_state.current_conversation_id == conversation_id:
        temp_conversation = _create_temp_conversation()
        st.session_state.current_conversation_id = temp_conversation["conversation_id"]
        st.session_state.current_conversation_title = temp_conversation["conversation_title"]
        st.session_state.messages.clear()
        # if len(st.session_state.conversation_list) > 0:
        #     _load_conversation_to_main_chatbot(
        #         st.session_state.conversation_list[0]
        #     )
        # else:
        #     st.session_state.current_conversation_id = None
    # del st.session_state.conversation_list[conversation_index]

    remove_conversation_id_by_userid(
        userid=st.session_state.user_id,
        conversationid=conversation_id
    )
    st.session_state.conversation_chatbot.embedder.delete_doc(conversation_id)

    # 마지막 대화가 삭제되었을 때, 새로운 대화를 생성
    # if len(st.session_state.conversation_list) == 0:
    #     _create_conversation()


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
    # st.session_state.conversation_list.insert(0, conversation)
    # 생성된 대화를 로드
    _load_conversation_to_main_chatbot(conversation)
    st.rerun()


def _create_temp_conversation():
    conversation = {
        "conversation_title": "임시 대화창",
        "conversation_id": "temp_conversation",
        "last_modified": datetime.datetime.now()
    }
    # no insert to list & no load from db because of temp conversation
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


def get_conversation_by_id(conversation_id):
    for conversation_index, conversation_item in enumerate(st.session_state.conversation_list):
        if conversation_item["conversation_id"] == conversation_id:
            return conversation_item
    return None


def _conversation_tab_area(conversation_tab):
    with conversation_tab:
        # create new converstation button
        if st.button("Create New Conversation", use_container_width=True):
            _create_conversation()
            # _load_conversation_to_main_chatbot(
            #     st.session_state.conversation_list[0]
            # )
            pass

        # st.markdown("""---""")

        for conversation_index, conversation_item in enumerate(st.session_state.conversation_list):
            conversation_id = conversation_item["conversation_id"]

            # Create columns
            col1, col2 = st.columns([6, 1])

            with col1:
                if st.button(conversation_item["conversation_title"], key=f"button_{conversation_id}",
                             use_container_width=True):
                    _load_conversation_to_main_chatbot(conversation_item)
                    # st.write(f"Default functionality for {conversation_id}")

            with col2:
                if st.button("🗑️", key=f"delete_{conversation_id}", use_container_width=True):
                    # st.write(f"Delete {conversation_id}")
                    _remove_conversation(conversation_id)
                    st.rerun()
            pass
    pass


def _search_tab_area(search_tab):
    with search_tab:
        with st.container(height=600, border=True):
            for message in st.session_state.conversation_messages:
                st.chat_message(message["role"]).markdown(message["content"])
                if message["role"] == "AI" and "conversation_link_buttons" in message:
                    with st.expander("Conversations", expanded=True):
                        for conversation_link_button_context in message["conversation_link_buttons"]:
                            conversation_id = conversation_link_button_context["id"]
                            conversation = get_conversation_by_id(
                                conversation_id)
                            conversation_link_button_key = conversation_link_button_context["key"]
                            if conversation is not None:
                                if st.button(conversation["conversation_title"], key=conversation_link_button_key, use_container_width=True):
                                    _load_conversation_to_main_chatbot(
                                        conversation)
                            else:


<< << << < HEAD
                                st.button(
                                    "대화 삭제됨", key=conversation_link_button_key, disabled=True)
== == == =
                                st.button("대화 삭제됨", key=conversation_link_button_key,
                                          disabled=True, use_container_width=True)
>>>>>> > 5f3ecf1d8c0e48c1028479e9d3fa57ec76e471bb

            conversation_message_human_ph = st.empty()
            conversation_message_ai_ph = st.empty()
            conversation_message_link_ph = st.empty()

        if prompt := st.chat_input("Conversation search"):
            chatbot = st.session_state.conversation_chatbot

            conversation_message_human_ph.chat_message(
                "Human").markdown(prompt)
            st.session_state.conversation_messages.append(
                {"role": "Human", "content": prompt})

            natural_response, parsed_response = chatbot.query(prompt)
            conversation_message_ai_ph.chat_message(
                "AI").markdown(natural_response)

            # st.session_state.conversation_messages.append({"role": "AI", "content": natural_response})
            ai_message = {"role": "AI", "content": natural_response}

            if "results" in parsed_response:
                conversation_link_button_list = []
                with conversation_message_link_ph.expander("Conversations", expanded=True):
                    for result in parsed_response["results"]:
                        conversation_id = str(result["conversation_id"])
                        conversation = get_conversation_by_id(conversation_id)
                        conversation_link_button_key = "conversation_link_button" + \
                                                       str(st.session_state.conversation_link_count)
                        if st.button(conversation["conversation_title"], key=conversation_link_button_key, use_container_width=True):
                            _load_conversation_to_main_chatbot(conversation)

                        conversation_link_button_list.append(
                            {"id": conversation_id, "key": conversation_link_button_key})
                        st.session_state.conversation_link_count += 1
                ai_message["conversation_link_buttons"] = conversation_link_button_list

            st.session_state.conversation_messages.append(ai_message)
    pass


def _settings_tab_area(settings_tab):
    with settings_tab:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.clear()
            st.success("로그아웃 되었습니다.")
            sleep(0.5)
            st.switch_page("login/app.py")
            pass

        with st.expander("모든 대화 삭제"):
            st.error("정말로 모든 대화를 삭제하시겠습니까?")
            if st.button("확인", key="delete_all_conversations", use_container_width=True):
                for conversation in st.session_state.conversation_list:
                    _remove_conversation(conversation["conversation_id"])
                st.session_state.conversation_list.clear()
                st.success("모든 대화가 삭제되었습니다.")
                st.rerun()

        with st.expander("회원탈퇴"):
            st.error("정말로 회원탈퇴를 하시겠습니까?")
            st.error("이 작업은 되돌릴 수 없습니다.")
            if st.button("확인", key="delete_account", use_container_width=True):
                for conversation in st.session_state.conversation_list:
                    _remove_conversation(conversation["conversation_id"])
                delete_user(st.session_state.user_id)
                st.session_state.clear()
                st.success("회원탈퇴가 완료되었습니다.")
                sleep(0.5)
                st.switch_page("login/app.py")


def sidebar_area():
    with st.sidebar:
        conversation_tab, search_tab, settings_tab = st.tabs(
            ["Conversation", "Search", "Settings"])

        _conversation_tab_area(conversation_tab)
        _search_tab_area(search_tab)
        _settings_tab_area(settings_tab)

    pass


if __name__ == "__main__":
    sidebar_area()
