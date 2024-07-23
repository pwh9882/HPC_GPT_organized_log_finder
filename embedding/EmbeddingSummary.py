from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
import streamlit as st
import threading
import os


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
        
        # >>>>>>>>>>>>>>>>>>> load or create vector db()
        # vector db를 가지고 있는 것을 주는 함수를 구현해야 함
        
        # self.vectorstore = FAISS(self.embeddings) # init 단계에서 vector_db를 load해와서 추후 load or create에서 참조가 됨
        
        self.index_path = "인덱스 file_경로" # 인덱스 파일 경로
        self.__initialized = True # vec Store 객체 initialization 완료 시 true
        
    def embed_and_store_summary(self, summary: str, user_id: str, conversation_id: str):
        # embedding = self.embeddings.embed([summary])
        metadata = {"user_id": user_id, "conversation_id": conversation_id}
    
        # self.load_or_create_vector_db(user_id, conversation_id) # 벡터 스토어를 로드 or 새로 생성 # >>>>>>>>>>>>>>수정해야함
        
        self.vectorstore.add_texts([summary], embeddings=self.embeddings, metadatas=[metadata]) # 
        
        self.vectorstore.save_local(self.index_path) # 업데이트된 벡터스토어를 저장

    def get_vector_db(self) :
        return self.vectorstore
        
    def load_or_create_vector_db(self):
        # vec store의 존재 여부를 먼저 파악
        if os.path.exists(self.index_path) :
            self.vectorstore = FAISS.load_local(self.index_path, self.embeddings) # 있음 -> 파일경로에서 인덱스 파일 load
        else:
            self.vectorstore = FAISS(self.embeddings) # 없음 -> 새로운 vec store 추가
            # <<이쪽에 save local logic 추가>>
            
            
        # 사용자 ID와 대화 ID에 해당하는 엔트리가 벡터 스토어에 존재하는지 chk하는 logic
        # existing_entries = self.vectorstore.search({"user_id": user_id, "conversation_id": conversation_id}) # 기존 DB 로드
        # existing_entries = self.vectorstore.search({"user_id": user_id, "conversation_id": conversation_id}) # 기존 DB 로드
        # if not existing_entries:
        #     self.vectorstore = FAISS(self.embeddings)  # 새로운 DB 생성
        
        # return self.vectorstore
    
    
