import faiss
import numpy as np
import sqlite3
import os
import torch
from transformers import AutoTokenizer, AutoModel

# 모델과 토크나이저 불러오기 (예: BERT 사용)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased") # <사전 학습된 BERT 토크나이저> 이 토크나이저는, 텍스트 --> 토큰 변환
model = AutoModel.from_pretrained("bert-base-uncased") # <사전 학습된 BERT 모델> 토큰 --> 임베딩 벡터로 변환

# 임베딩 생성
def embed_text(text): 
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512) # 텍스트를 토큰화하고 모델 입력 형식으로 변환
    with torch.no_grad(): # no gradient --> 기울기 계산 아니하여 모델 추론
        outputs = model(**inputs)
    # 마지막 히든 스테이트를 가져와서 평균값으로 임베딩 생성
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy() # 마지막 히든 스테이트를 가져와서 각 토큰의 임베딩 벡터의 평균을 계산하여 하나의 벡터로 만듦
    return embeddings

# 임베딩 저장
def save_session_summary(conversation_id, summary, db_path="vector_db.index", sqlite_path="sessions.db"):
    embedding = embed_text(summary) # 임베딩 생성
    
    # FAISS 벡터 DB에 저장
    if not os.path.exists(db_path):
        d = embedding.shape[0]  # 임베딩 벡터의 차원
        index = faiss.IndexFlatL2(d)  # L2 거리 기반 인덱스
    else:
        index = faiss.read_index(db_path)
    
    index.add(np.array([embedding]))
    faiss.write_index(index, db_path)
    
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
