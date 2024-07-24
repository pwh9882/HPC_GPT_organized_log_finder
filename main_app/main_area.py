import threading

import streamlit as st


def main_area():
    # title
    st.title(st.session_state.current_conversation_id)

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Message"):
        chatbot = st.session_state.main_chatbot

        user_id = st.session_state.user_id
        conversation_id = st.session_state.current_conversation_id

        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "Human", "content": prompt})

        with st.spinner("Generating Response..."):
            response = chatbot.invoke_chain(prompt, user_id, conversation_id)

            # summary = st.session_state.main_chatbot.get_conversation_summary(
            #     user_id, conversation_id
            # )
            # st.session_state.summary_embedder.embed_and_store_summary(
            #     summary, user_id, conversation_id
            # )

            # Display assistant response in chat message container
            with st.chat_message("AI"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "AI", "content": response})

            def summarize_and_embedding(user_id, conversation_id, main_chatbot, embedder):
                summary = main_chatbot.get_conversation_summary(user_id, conversation_id)
                print(summary)

                vectorstore = embedder.get_vector_db()
                prev_doc = vectorstore.get(ids=[conversation_id])
                print(prev_doc)
                if len(prev_doc['ids']) != 0:
                    print("update")
                    embedder.update_doc(summary, user_id, conversation_id)
                else:
                    print("add")
                    embedder.embed_and_store_summary(summary, user_id, conversation_id)

            print("start")
            main_chatbot = st.session_state.main_chatbot
            embedder = st.session_state.summary_embedder
            thread = threading.Thread(target=summarize_and_embedding,
                                      args=(user_id, conversation_id, main_chatbot, embedder))
            thread.start()
            print("end")

    pass


if __name__ == "__main__":
    main_area()
