from llama_index.core.memory import Memory
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.chat_engine import SimpleChatEngine, CondenseQuestionChatEngine, ContextChatEngine, CondensePlusContextChatEngine

def get_simple_chat_engine(llm, memory=None, prefix_messages=None):
    memory = memory or Memory.from_defaults(token_limit=1000)
    prefix_messages = prefix_messages or [ChatMessage(content="You are a helpful assistant.", role=MessageRole.SYSTEM)]
    chat_engine = SimpleChatEngine(llm=llm, memory=memory, prefix_messages=prefix_messages)
    return chat_engine

def get_condense_question_chat_engine(llm, index, memory=None):
    memory = Memory.from_defaults(token_limit=500)
    #embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Empty Index with embedding model specified
    #index = VectorStoreIndex.from_documents([], embed_model=embed_model)
    query_engine = index.as_query_engine(llm=llm, memory=memory)
    chat_engine = CondenseQuestionChatEngine(
                    query_engine=query_engine, condense_question_prompt=None,
                    memory = memory, llm = llm)

    return chat_engine


def get_context_chat_engine(llm, index,memory=None,prefix_messages=None):
    memory = Memory.from_defaults(token_limit=500)
    retriever = index.as_retriever()
    retriever.mode = "default"
    system_prompt = "You are a helpful assistant. ONLY answer based on the provided context. If you don't know, say 'I don't know'."
    prefix_messages = prefix_messages or [ChatMessage(content=system_prompt, role=MessageRole.SYSTEM)]
    chat_engine = ContextChatEngine(
                    retriever=retriever, prefix_messages=prefix_messages,
                    memory = memory, llm = llm)

    return chat_engine

def get_condense_plus_context_chat_engine(llm, index,memory=None,prefix_messages=None):
    memory = Memory.from_defaults(token_limit=500)
    #embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniL-ML6-v2")
    # Empty Index with embedding model specified
    #index = VectorStoreIndex.from_documents([], embed_model=embed_model)
    retriever = index.as_retriever()
    prefix_messages = prefix_messages or [ChatMessage(content="You are a helpful assistant.", role=MessageRole.SYSTEM)]
    chat_engine = CondensePlusContextChatEngine(retriever=retriever, llm=llm,memory=memory)
    return chat_engine