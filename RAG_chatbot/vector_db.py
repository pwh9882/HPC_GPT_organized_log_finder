import faiss
import numpy as np
import sqlite3

# 벡터 DB 초기화
def initialize_faiss():
    dimension = 512  # 임베딩 벡터의 차원
    index = faiss.IndexFlatL2(dimension)
    return index

# 벡터 DB에 임베딩 추가
def add_embedding(index, embedding, conversation_id):
    index.add(np.array([embedding], dtype=np.float32))
    # 인덱스를 관리하기 위해 conversation_id를 별도로 저장
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO faiss_index (conversation_id, embedding)
        VALUES (?, ?)
    ''', (conversation_id, embedding.tobytes()))
    conn.commit()
    conn.close()

# 임베딩 벡터를 검색
def search_embedding(index, query_embedding, k=5):
    distances, indices = index.search(np.array([query_embedding], dtype=np.float32), k)
    return distances, indices
