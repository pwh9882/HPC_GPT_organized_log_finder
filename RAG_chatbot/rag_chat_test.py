from rag_test2 import RAGChatbot


def main():
    chatbot = RAGChatbot()

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("=============")
            print("챗봇을 종료합니다.")
            print("=============")
            break
        chatbot.query(user_input)


if __name__ == "__main__":
    chatbot = RAGChatbot()
    # print(chatbot.query(
    #     "채팅 기록과 최신 질문에 대한 관련 대화 내용이 있었는데, 찾아줄래? 그리고 그 대화의 메타데이터 중 conversationid 값이 얼마인지 알려줘"))
    # print(chatbot.query(
    #     "FAISS에 대한 관련 대화 내용이 있었는데, 찾아줄래? 그리고 그 대화의 메타데이터 중 conversationid 값이 얼마인지 알려줘"))
    # main()
    print(chatbot.query(
        "FAISS와 LangChain에 대한 관련 대화 내용이 있었는데, 찾아줄래?"
    ))
