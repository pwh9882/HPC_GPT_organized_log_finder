from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationSummaryMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.utils import ConfigurableFieldSpec
from typing import List, Dict, Any
import threading

from langchain_openai import AzureChatOpenAI
import streamlit as st


class SQLSummaryChatBot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SQLSummaryChatBot, cls).__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.llm = AzureChatOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version=st.secrets["OPENAI_API_VERSION"],
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
            model=st.secrets["AZURE_OPENAI_DEPLOYMENT"]
        )

        self._init_chain_()

        self.summary_memory = ConversationSummaryMemory(
            llm=self.llm,
            return_messages=True,
        )
        self.__initialized = True

    def _init_chain_(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        self.chain = prompt | self.llm | StrOutputParser()

        config_fields = [
            ConfigurableFieldSpec(
                id="user_id",
                annotation=str,
                name="User ID",
                description="Unique identifier for a user.",
                default="",
                is_shared=True,
            ),
            ConfigurableFieldSpec(
                id="conversation_id",
                annotation=str,
                name="Conversation ID",
                description="Unique identifier for a conversation.",
                default="",
                is_shared=True,
            ),
        ]

        self.chain_with_history = RunnableWithMessageHistory(
            self.chain,
            get_session_history=self.get_chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            history_factory_config=config_fields,
        )

    def get_chat_history(self, user_id: str, conversation_id: str) -> SQLChatMessageHistory:
        return SQLChatMessageHistory(
            table_name=user_id,
            session_id=conversation_id,
            connection="sqlite:///chat_history.db",
        )

    def get_conversation_summary(self, user_id: str, conversation_id: str) -> str:
        chat_history = self.get_chat_history(user_id, conversation_id).messages
        return self.summary_memory.predict_new_summary(messages=chat_history, existing_summary="")

    def get_conversation_title(self, user_id: str, conversation_id: str) -> str:
        config = {
            "configurable": {
                "user_id": user_id,
                "conversation_id": conversation_id
            }
        }

        chat_history = self.get_chat_history(user_id, conversation_id).messages
        # return self.chain.invoke({"chat_history": chat_history, "input": 'Create a title that fits this conversation'}, config)
        return self.chain.invoke({"chat_history": chat_history, "input": '이 대화 내용에 어울리는 아주 짧은 제목을 만들어'}, config)

    def invoke_chain(self, input_text: str, user_id: str, conversation_id: str) -> str:
        config = {
            "configurable": {
                "user_id": user_id,
                "conversation_id": conversation_id
            }
        }

        response = self.chain_with_history.invoke(
            {"input": input_text}, config
        )
        return response
