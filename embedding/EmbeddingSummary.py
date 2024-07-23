from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
import streamlit as st
import threading

# singleton으로 구현. vector_db에 하나만 유지하기 위하여 singleton으로 instance가 두 개 이상 생성되는 것을 방지함. 이를 위해 init을 통해 vector를 가지고 있음
class EmbeddingSummary:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(EmbeddingSummary, cls).__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return

        openai.api_key = st.secrets["AZURE_OPENAI_API_KEY"]
        openai.api_base = st.secrets["AZURE_OPENAI_ENDPOINT"]
        openai.api_version = st.secrets["OPENAI_API_VERSION"]
        openai.api_type = 'azure'

        self.embeddings = AzureOpenAIEmbeddings(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            model=st.secrets["AZURE_OPENAI_DEPLOYMENT"]
        )
        
        self.vectorstore = FAISS(self.embeddings) # init 단계에서 vector_db를 load해와서 추후 load or create에서 참조가 됨
        self.__initialized = True # vec Store 객체 initialization 완료 시 true

    def embed_and_store_summary(self, summary: str, user_id: str, conversation_id: str):
        embedding = self.embeddings.embed([summary])
        metadata = {"user_id": user_id, "conversation_id": conversation_id}
        self.vectorstore.add_texts([summary], embeddings=embedding, metadatas=[metadata]) # vectorStore에 [요약문] [임베딩] [meta data] 추가

    def load_or_create_vector_db(self, user_id: str, conversation_id: str):
        existing_entries = self.vectorstore.search({"user_id": user_id, "conversation_id": conversation_id})
        if existing_entries:
            return self.vectorstore  # 기존 DB 로드
        else:
            self.vectorstore = FAISS(self.embeddings)  # 새로운 DB 생성
            return self.vectorstore
