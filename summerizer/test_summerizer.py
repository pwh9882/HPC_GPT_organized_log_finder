from summerizer import SQLSummaryChatBot


def invoke_test():
    chatbot = SQLSummaryChatBot()
    response = chatbot.invoke_chain(
        "Guess What times I introduced myself.", "user1", "conversation1")
    print(response)
    """
    You introduced yourself twice. Is there something specific you'd like to discuss or need help with?
    """


def history_test():
    chatbot = SQLSummaryChatBot()
    history = chatbot.get_chat_history("user1", "conversation1").messages
    for message in history:
        print(message)
    """
    content='Hello, my name is Alice.'
    content='Hello, Alice! How can I assist you today?' 
    content='Hello, my name is Alice.'
    content='Hi again, Alice! How can I help you today?'
    content="What's my name?"
    content='Your name is Alice. How can I assist you further?'
    content='Guess What times I introduced myself.'
    content="You introduced yourself twice. Is there something specific you'd like to discuss or need help with?"
    """


def summary_test():
    chatbot = SQLSummaryChatBot()
    summary = chatbot.get_conversation_summary("user1", "conversation1")
    print(summary)
    """
    Alice introduces herself to the AI and asks for assistance. 
    She repeats her introduction, and the AI recognizes her name. 
    Alice asks the AI to guess how many times she introduced herself, 
    and the AI correctly states it was twice, then asks if there's anything specific she needs help with.
    """


if __name__ == "__main__":
    # invoke_test()
    # history_test()
    summary_test()
    pass
