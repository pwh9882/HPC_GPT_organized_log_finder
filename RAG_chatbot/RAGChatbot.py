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

from embedding.SummaryEmbedder import SummaryEmbedder


class RAGChatbot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RAGChatbot, cls).__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self.__initialized:
            return

        self.embedder = SummaryEmbedder()
        self._load_vector_db_()
        # self._load_dummy_vector_db_()
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
                You are an assistant for question-answering tasks. 
                Use the following pieces of retrieved context to answer the question.
                If you cannot find the answer in the retrieved context, try to find it in chat history.
                If you don't know the answer after all, just say that you don't know. 

                Your response should be in the following format:
                ---
                Natural language response to the user's query.
                ---
                JSON_DATA: {{
                    "results": [
                        {{
                            "summary": "A brief summary of the found information (1-2 sentences)",
                            "conversation_id": integer
                        }},
                        // ... more results if available
                    ]
                }}

                Provide a natural language response for the user, followed by a JSON structure 
                containing summaries and conversation_ids for each relevant piece of information found.
                If no relevant information is found, omit the JSON_DATA section.

                Context: {context}
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

    def query(self, user_input: str) -> str:
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
        return parsed_response["natural_response"]
