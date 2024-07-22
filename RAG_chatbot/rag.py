from .vector_db import initialize_faiss, add_embedding, search_embedding
from .gpt_model import generate_response
from db import get_all_conversation_id_by_userid
import numpy as np

# 벡터 DB 초기화
faiss_index = initialize_faiss()

# 사용자 대화 요약 임베딩을 벡터 DB에 추가
def add_summary_embedding(user_id, conversation_id, summary):
    # 임베딩 생성 (여기서는 예시로 랜덤 벡터를 사용)
    embedding = np.random.rand(512).astype(np.float32)
    add_embedding(faiss_index, embedding, conversation_id)

# 검색 및 응답 생성
def retrieve_and_generate(user_id, query):
    # 사용자의 모든 대화 요약본을 검색
    summaries = get_all_conversation_id_by_userid(user_id)
    # 쿼리 임베딩 생성 (여기서는 예시로 랜덤 벡터를 사용)
    query_embedding = np.random.rand(512).astype(np.float32)
    distances, indices = search_embedding(faiss_index, query_embedding)
    
    # 가장 유사한 대화 요약본을 찾음
    closest_summary = summaries[indices[0][0]]
    
    # GPT-4를 사용하여 응답 생성
    response = generate_response(f"Based on the following summary: {closest_summary}\nUser query: {query}")
    return response
