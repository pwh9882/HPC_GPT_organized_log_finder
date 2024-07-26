import threading

from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings

import streamlit as st

from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder

from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory

# for _load_dummy_vector_db_
from langchain_core.documents import Document

import json
from typing import Any, Dict

from RAG_chatbot.embedding.SummaryEmbedder import SummaryEmbedder


class RAGChatbot:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, user_id, *args, **kwargs):
        if user_id not in cls._instances:
            with cls._lock:
                if user_id not in cls._instances:
                    instance = super(RAGChatbot, cls).__new__(cls)
                    instance.__initialized = False
                    cls._instances[user_id] = instance
        return cls._instances[user_id]

    def __init__(self, user_id: str) -> None:
        if self.__initialized:
            return

        self.user_id = user_id
        self.embedder = SummaryEmbedder()
        self._load_vector_db_()
        self._load_rag_model_()
        self.__initialized = True

    def _load_vector_db_(self):
        self.vector_db = self.embedder.get_vector_db()

    def _load_rag_model_(self):
        self.rag_chain = self._create_rag_chain_()

    def _create_rag_chain_(self):
        llm = AzureChatOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version=st.secrets["OPENAI_API_VERSION"],
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
            model=st.secrets["AZURE_OPENAI_DEPLOYMENT"]
        )

        retriever = self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4, "filter": {"user_id": self.user_id}}
        )

        def retrieve_and_prepare_context(input_dict):
            print("retrieve_and_prepare_context...")
            query = input_dict["query"]
            chat_history = input_dict["chat_history"]

            # Use chat history to refine the query
            if chat_history:
                context_query = f"Given the following chat history and the current question, generate a search query:" + \
                    f"\n\nChat History:\n{chat_history}\n\n" + \
                    f"Current Question: {query}\n\nRefined Query:"
                refined_query = llm.predict(context_query)
            else:
                refined_query = query
            print("Refined Query:", refined_query)
            results = retriever.invoke(refined_query)
            context_blocks = []
            for doc in results:
                content = doc.page_content
                metadata = doc.metadata
                context_blocks.append(
                    f"Content: {content}\nMetadata: {metadata}")
            context = "\n\n".join(context_blocks)
            # print(context)
            return {"context": context, "query": query}

        qa_system_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """
                 
                #Your task
                You are a capable natural language search engine that finds documents for the user within context. 
                Do not interpret the user's input as a general response from an LLM, but rather as a question to find the relevant conversation session.
                Use the following pieces of retrieved context to answer the question.
                You MUST use the retrieved context to answer the question.
                If you don't know the answer after all, just say that you don't know.

                Your response should be in the following format:
                
                #Example
                Natural language response to the user's query.
                (What you found)
                
                (And so on for each relevant piece of information (1-2 sentences))
                JSON_DATA: {{
                    "results": [
                        {{
                            "summary": "A brief summary of the found information (1-2 sentences)",
                            "conversation_id": string
                        }},
                        // ... more results if available
                    ]
                }}
                
                ##and here is an example:
                당신의 이름이 언급된 채팅은 다음과 같습니다.
                
                이 채팅에서 당신은 한국어로 자신을 소개했고, AI는 한국어로 당신을 인사하며 만나서 기쁘다고 표현하고 오늘 어떻게 도와드릴 수 있는지 물었습니다.
                JSON_DATA: {{
                    "results": [
                        {{
                            "summary": "The human introduces themselves as Sarah in Korean. The AI greets Sarah in Korean, expresses pleasure in meeting her, and asks how it can assist her today.",
                            "conversation_id": "5f2740d5-6c3f-4afb-be2e-7bfe87577030"
                        }}
                    ]
                }}
                
                ##and this is when muilple results are found:
                다음은 LLM에 관한 채팅입니다.

                첫 번째 채팅에서는 사용자가 AI에게 LLM에 대해 간단히 설명해달라고 요청했고, AI는 LLM이 "Large Language Model"의 약자로, 대규모 데이터셋을 학습하여 인간과 같은 텍스트를 생성하거나 이해할 수 있는 AI 모델이라고 설명했습니다. 이러한 모델은 번역, 요약, 질문 응답, 대화 생성 등 다양한 자연어 처리 작업에 사용되며, OpenAI의 GPT-3가 그 예로 언급되었습니다.

                두 번째 채팅에서도 사용자가 LLM 모델에 대해 묻자, AI는 LLM (Large Language Models)이 자연어 처리를 위해 설계된 AI 모델로, 방대한 양의 텍스트 데이터를 학습하여 인간과 같은 언어를 이해하고 생성할 수 있다고 설명했습니다. 예로는 OpenAI의 GPT-3, Google's BERT, Meta's LLaMA가 언급되었으며, 이러한 모델들은 번역, 요약, 질문 응답, 텍스트 생성과 같은 작업에 사용된다고 설명했습니다. 모델의 성능은 주로 파라미터 수와 학습 데이터 양에 의해 결정됩니다.
                JSON_DATA: {{
                    "results": [
                        {{
                            "summary": "The user asked the AI to explain LLM, and the AI described it as an abbreviation for 'Large Language Model' that can generate or understand human-like text by training on large datasets. The AI mentioned that such models are used for various NLP tasks like translation, summarization, question-answering, and conversation generation, and cited OpenAI's GPT-3 as an example.",
                            "conversation_id": "5f2740d5-6c3f-4afb-be2e-7bfe87577030"
                        }},
                        {{
                            "summary": "The user inquired about LLM models again, and the AI explained that LLMs are AI models designed for natural language processing that can understand and generate human-like language by training on vast amounts of text data. Examples such as OpenAI's GPT-3, Google's BERT, and Meta's LLaMA were mentioned, and these models are used for tasks like translation, summarization, question-answering, and text generation. The performance of the models is primarily determined by the number of parameters and the amount of training data.",
                            "conversation_id": "5f2740d5-6c3f-4afb-be2e-7bfe87577030"
                        }}
                    ]
                }}
                
                ##and here is an example that you cannot find the answer:
                죄송합니다, 답변을 찾을 수 없습니다. 제가 찾을 수 있도록 더 정보를 주실 수 있을까요?
                JSON_DATA: {{
                    "results": []
                }}

                
                #Instructions
                Provide a natural language response for the user, followed by a JSON structure 
                containing summaries and conversation_ids for each relevant piece of information found.
                If no relevant information is found, omit the JSON_DATA section.
                
                #Context
                Answer must refer to the retrieved context(it can be empty, it means there is no document found.): {{
                    {context}
                }}
                
                #Last Note
                If you don't know the answer after all, just say that you don't know.
                DO NOT GENERATE A RESPONSE WITHOUT USING THE CONTEXT.
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{query}"),
            ]
        )

        memory = ConversationBufferMemory(
            chat_memory=InMemoryChatMessageHistory(),
            return_messages=True,
            memory_key="chat_history"
        )

        def process_query(input_dict):
            print("process_query...")
            query = input_dict["query"]
            chat_history = memory.chat_memory.messages
            return {"query": query, "chat_history": chat_history}

        rag_chain = (
            RunnablePassthrough()
            | RunnableLambda(process_query)
            | RunnableParallel(
                {"context_and_query": retrieve_and_prepare_context,
                 "chat_history": lambda x: x["chat_history"]}
            )
            | (lambda x: {**x["context_and_query"], "chat_history": x["chat_history"]})
            | qa_system_prompt
            | llm
            | StrOutputParser()
        )

        def update_memory(input_dict):
            query = input_dict["query"]
            output = input_dict["output"]
            memory.chat_memory.add_user_message(query)
            memory.chat_memory.add_ai_message(output)
            return output

        return RunnablePassthrough() | RunnableParallel(
            {"query": lambda x: x["query"], "output": rag_chain}
        ) | RunnableLambda(update_memory)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        parts = response.split("JSON_DATA:", 1)
        natural_response = parts[0].strip()
        json_data = {}
        if len(parts) > 1:
            try:
                json_data = json.loads(parts[1].strip())
            except json.JSONDecodeError:
                pass
        return {"natural_response": natural_response, "json_data": json_data}

    def query(self, user_input: str) -> list[str, str]:
        raw_response = self.rag_chain.invoke({"query": user_input})
        print("raw_response:", raw_response)

        parsed_response = self._parse_response(raw_response)
        print("parsed_response:", parsed_response)

        # Update the current conversation IDs
        self.current_conversation_ids = [
            result["conversation_id"]
            for result in parsed_response["json_data"].get("results", [])
        ]

        # Return only the natural language response to the user
        return parsed_response["natural_response"], parsed_response['json_data']
