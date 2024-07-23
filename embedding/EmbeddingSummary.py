from langchain.embeddings import AzureOpenAIEmbeddings
# from langchain.vectorstores import Chroma
from langchain.vectorstores import Chroma
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
        
        self.index_path = "인덱스 file_경로3" # 인덱스 파일 경로
        
        self.load_or_create_vector_db()  # init 단계에서 load or create vector db()에 대한 것 반영. 초기화 시 벡터스토어를 로드하거나 생성
        
        self.__initialized = True # vec Store 객체 초기화 완료 flag

    def embed_and_store_summary(self, summary: str, user_id: str, conversation_id: str):
        metadata = {"user_id": user_id, "conversation_id": conversation_id}
    
        self.vectorstore.add_texts([summary], embeddings=self.embeddings, metadatas=[metadata]) # 
        self.vectorstore.save_local(self.index_path) # 업데이트된 벡터스토어를 저장

    def get_vector_db(self) : # vectorstore에 대한 getter
        return self.vectorstore
        
    def load_or_create_vector_db(self):
        # vec store의 존재 여부를 먼저 파악
        if os.path.exists(self.index_path) :
            # self.vectorstore = Chroma.load_local(self.index_path, self.embeddings) # 있음 -> 파일경로에서 인덱스 파일 load
            self.vectorstore = Chroma(persist_directory=self.index_path, embedding_function=self.embeddings)
        else:
            self.vectorstore = Chroma(embedding_function=self.embeddings) # 없음 -> 새로운 vec store 추가
            
            # 이쪽에서도 save_local 해야 함
            # self.vectorstore.save_local(self.index_path)
            # Chroma(persist_directory=self.index_path)
            self.vectorstore.persist()
    
    def get_conversation_id(self, user_id: str, conversation_id: str) -> str:
        return f"{user_id}_{conversation_id}"
    
    
    # 세션이 추가됨에 따른 update와 delete
    def update_conversation(self, conversation_id: str, new_summary: str):
        conversation_id.get_conversation_id()
        # conversation_id를 기준으로 기존 데이터를 검색
        result = self.vectorstore.search({"conversation_id": conversation_id})
        # new_summary
        # example_db.update_document(ids[0], docs[0])
        # get
        
        self.vectorstore.update_text(result["id"], new_summary, {"conversation_id": conversation_id})
    
    def update_conversation(self, new_summary: str, metadata = {conversation_id: str, user_id: str}):
        doc_id = self.get_conversation_id(user_id, conversation_id)
        
        # conversation_id를 기준으로 기존 데이터를 검색
        result = self.vectorstore._collection.get(ids=[doc_id])
        
        if result['metadatas']:
            metadata = result['metadatas'][0]
            metadata["updated"] = True
            
            # DB 업데이트
            self.vectorstore._collection.update(ids=[doc_id], documents=[new_summary], metadatas=[metadata])
            self.vectorstore.persist()  # 업데이트된 벡터스토어를 저장

    def delete_conversation(self, user_id: str, conversation_id: str):
        # doc_id = self.get_conversation_id(user_id, conversation_id)
        
        # 문서 삭제
        self.vectorstore._collection.delete(ids=[conversation_id])
        self.vectorstore.persist()

            
        