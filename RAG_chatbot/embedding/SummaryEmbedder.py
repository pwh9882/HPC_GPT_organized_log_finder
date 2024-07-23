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

    def get_vector_db(self):  # vectorstore에 대한 getter
        return self.vectorstore

    def load_or_create_vector_db(self):
        self.vectorstore = Chroma(
            persist_directory=self.index_path, embedding_function=self.embeddings
        )

    def embed_and_store_summary(self, summary: str, user_id: str, conversation_id: str):
        metadata = {"user_id": user_id, "conversation_id": conversation_id}

        doc = Document(page_content=summary, metadata=metadata)
        self.vectorstore.add_documents(
            [doc], embeddings=self.embeddings, ids=[conversation_id]
        )

    def update_doc(self, new_summary: str, user_id: str, conversation_id: str):

        prev_doc = self.vectorstore.get(ids=[conversation_id])

        if prev_doc:
            new_doc = Document(page_content=new_summary, metadata={
                               "user_id": user_id, "conversation_id": conversation_id})

            self.vectorstore.update_document(conversation_id, new_doc)

    def delete_doc(self, conversation_id: str):
        self.vectorstore._collection.delete(ids=[conversation_id])

    def add_dummy_data(self):
        list_of_summary = [
            "이 대화는 FAISS 인덱스를 로드하려고 시도하고, 인덱스가 존재하지 않으면 새로운 인덱스를 생성하고 저장하는 방법에 대한 것입니다. 코드는 주어진 경로에 인덱스가 존재하면 로드하고, 존재하지 않으면 데이터를 사용하여 새로운 인덱스를 생성한 후 저장하도록 구성되어 있습니다.",
            """
                     ### 대화 요약

이 대화에서는 LangChain에서 LLM이 Retrieval 과정을 통해 문서와 메타데이터를 함께 읽고, 답변을 생성할 때 이를 포함하여 출력하는 방법에 대해 설명하였습니다. 주요 내용은 다음과 같습니다:

1. **Retriever 설정**: 문서와 메타데이터를 함께 저장하고 검색하는 방법.
2. **LLM 설정 및 메타데이터 표시**: 검색 결과와 메타데이터를 포함하여 LLM이 출력하도록 설정.
3. **LLM 템플릿에 메타데이터 포함**: 문서 내용과 메타데이터를 템플릿에 포함시켜 LLM이 이를 참고하여 답변을 생성하도록 하는 방법.
4. **사용된 문서 추적**: LLM이 실제로 사용한 문서와 메타데이터를 정확히 추적하고 표시하는 커스텀 체인 구현 방법.

이를 통해 LangChain에서 LLM이 메타데이터를 읽고 사용할 수 있게 함으로써 답변의 정확성을 높이고, 메타데이터 기반의 더 자세한 정보를 제공할 수 있는 방법을 논의하였습니다.
                     """,
            "이 대화는 사용자에게 채팅 기록과 최신 질문을 기반으로, 채팅 기록 없이도 이해할 수 있는 독립적인 질문을 다시 작성하는 방법에 대한 요청입니다."
        ]

        for idx, summary in enumerate(list_of_summary):
            self.embed_and_store_summary(
                summary, user_id="test", conversation_id=str(idx))


if __name__ == "__main__":
    embedder = SummaryEmbedder()
    embedder.add_dummy_data()
    print("Dummy data added.")
