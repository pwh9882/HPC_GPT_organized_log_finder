import os
import numpy as np
import sqlite3
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from transformers import AutoTokenizer, AutoModel
import streamlit as st

#AzureOpenAI
api_key=st.secrets["AZURE_OPENAI_API_KEY"],
api_version=st.secrets["OPENAI_API_VERSION"],
azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
model=st.secrets["AZURE_OPENAI_DEPLOYMENT"]


# 임베딩 생성
def embed_text(text):
    # OpenAIEmbeddings를 사용하여 임베딩을 생성
    embeddings = OpenAIEmbeddings()
    embedding_vector = embeddings.embed(text) # 분할없이 임베딩
    
    return np.array(embedding_vector)

# 임베딩 저장
def save_session_summary(conversation_id, summary, db_path="vector_db.index", sqlite_path="sessions.db"):
    embedding = embed_text(summary) # 임베딩 생성
    
    # FAISS 벡터 DB에 저장
    if not os.path.exists(db_path):
        d = embedding.shape[0]  # 임베딩 벡터의 차원
        index = FAISS.IndexFlatL2(d)  # L2 거리 기반 인덱스
    else:
        index = FAISS.read_index(db_path)
    
    index.add(np.array([embedding]))
    FAISS.write_index(index, db_path)
    
    # SQLite DB에 저장
    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (conversation_id TEXT, summary TEXT)''')
    c.execute("INSERT INTO sessions (conversation_id, summary) VALUES (?, ?)", (conversation_id, summary))
    conn.commit()
    conn.close()

# 예시
conversation_id = "ss123"
summary = "코딩을 잘 하고 싶은 고민과 그에 대한 답변"

# 세션 요약 및 저장
save_session_summary(conversation_id, summary)
