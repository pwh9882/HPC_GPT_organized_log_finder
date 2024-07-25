
from langchain_core.documents import Document
from SummaryEmbedder import SummaryEmbedder
# 테스트 함수 정의


def test_summary_embedder():
    embedder = SummaryEmbedder()

    # 테스트 데이터 설정
    summary1 = "This is a test summary"
    user_id1 = "user_1"
    conversation_id1 = "conv_1"

    summary2 = "This is an updated summary"

    print("Embedding and storing summary...")
    embedder.embed_and_store_summary(summary1, user_id1, conversation_id1)
    print("Stored summary:", embedder.get_vector_db().get(
        ids=[conversation_id1]))

    print("\nUpdating summary...")
    embedder.update_doc(summary2, user_id1, conversation_id1)
    print("Updated summary:", embedder.get_vector_db().get(
        ids=[conversation_id1]))

    # print("\nDeleting summary...")
    # embedder.delete_doc(conversation_id1)
    # print("Deleted summary:", embedder.get_vector_db().get(
    #     ids=[conversation_id1]))


def test2():
    embedder = SummaryEmbedder()
    print(embedder.get_vector_db().get(ids=["conv_1"]))


# 테스트 함수 실행
# test_summary_embedder()
test2()
