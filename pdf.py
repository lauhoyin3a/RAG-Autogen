import json
import os
import chromadb
import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
# Accepted file formats for that can be stored in
# a vector database instance
from autogen.retrieve_utils import TEXT_FORMATS


config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")

assert len(config_list) > 0
print("models to use: ", [config_list[i]["model"] for i in range(len(config_list))])

# 1. create an RetrieveAssistantAgent instance named "assistant"
assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config={
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
    },
)

# 2. create the RetrieveUserProxyAgent instance named "ragproxyagent"

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "code",
        "docs_path": [
            os.path.join("data", "2024-03-25-JPMorgan-Equity Strategy Equity PE multiples in historical context - earnings vs...-107204257.pdf"),
            os.path.join("data", "2024-03-25-Morgan Stanley-Asia Quantitative Strategy Biweekly Perspectives Rising Signs Of Marke...-107204434.pdf"),
            os.path.join("data", "2024-03-25-Morgan Stanley-US Equity Strategy Weekly Warm-up Great Expectations Suggest More Rota...-107204697.pdf"),
        ],
        "custom_text_types": ["mdx"],
        "chunk_token_size": 2000,
        "model": config_list[0]["model"],
        "client": chromadb.PersistentClient(path="/tmp/chromadb"),
        "embedding_model": "all-mpnet-base-v2",
        "get_or_create": True,  # set to False if you don't want to reuse an existing collection, but you'll need to remove the collection manually
    },
    code_execution_config=False,  # set to False if you don't want to execute the code
)

# reset the assistant. Always reset the assistant before starting a new conversation.
qa_problem = input("Please Enter The Question: ")
assistant.reset()
#qa_problem = "What's your overall recommendation related to global equity strategies?"
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=qa_problem)