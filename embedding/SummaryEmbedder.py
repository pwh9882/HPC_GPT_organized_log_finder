from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import streamlit as st
import threading


# singleton으로 구현. vector_db에 하나만 유지하기 위하여 singleton으로 instance가 두 개 이상 생성되는 것을 방지함. 이를 위해 init을 통해 vector를 가지고 있음
class SummaryEmbedder:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SummaryEmbedder, cls).__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return

        self.embeddings = AzureOpenAIEmbeddings(
            model=st.secrets["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
        )

        self.index_path = "./embedding.db"  # 인덱스 파일 경로

        # init 단계에서 load or create vector db()에 대한 것 반영. 초기화 시 벡터스토어를 로드하거나 생성
        self.load_or_create_vector_db()

        self.__initialized = True  # vec Store 객체 초기화 완료 flag

    def embed_and_store_summary(self, summary: str, user_id: str, conversation_id: str):
        metadata = {"user_id": user_id, "conversation_id": conversation_id}

        doc = Document(page_content=summary, metadata=metadata)
        self.vectorstore.add_documents(
            [doc], embeddings=self.embeddings, ids=[conversation_id]
        )

    def get_vector_db(self):  # vectorstore에 대한 getter
        return self.vectorstore

    def load_or_create_vector_db(self):
        self.vectorstore = Chroma(
            persist_directory=self.index_path, embedding_function=self.embeddings
        )

    def update_doc(self, new_summary: str, user_id: str, conversation_id: str):

        prev_doc = self.vectorstore.get(ids=[conversation_id])

        if prev_doc:
            new_doc = Document(page_content=new_summary, metadata={
                               "user_id": user_id, "conversation_id": conversation_id})

            self.vectorstore.update_document(conversation_id, new_doc)

    def delete_doc(self, conversation_id: str):
        self.vectorstore._collection.delete(ids=[conversation_id])
