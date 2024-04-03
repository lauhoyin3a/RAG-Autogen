import json
import os
import re
import requests
from dotenv import load_dotenv
import autogen
import chromadb
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.retrieve_utils import TEXT_FORMATS

load_dotenv()

config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")
SERP_API_KEY = os.getenv("SERP_API_KEY")

def add_data_resources(rag_agent, data_source):
    rag_agent._retrieve_config['docs_path'].append(data_source)


def agent_google_search(rag_agent, topic):
    retrieve_content = call_serpapi(topic)
    add_data_resources(rag_agent, os.path.join("data", retrieve_content))

def call_serpapi(query):
    api_key = os.getenv("SERP_API_KEY")
    base_url = "https://serpapi.com/search"
    params = {
        'q': query,
        'engine': 'google',
        'api_key': api_key,
        'output': 'json'
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            json_data = response.json()
            filename = f"{query}_result.json"
            filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
            filepath = os.path.join("data/google", filename)  # Update filepath to include the "data" directory
            with open(filepath, 'w') as file:
                json.dump(json_data, file, indent=4)
            print(f"Search results saved to {filepath}")
            return filepath
        else:
            print("Error: ", response.status_code)
    except requests.RequestException as e:
        print("Error: ", e)

def agent_report_search(rag_agent):
    for report in os.listdir('data/report'):
        add_data_resources(rag_agent, os.path.join("data/report", report))



def main():

    def reset_agents():
        assistant.reset()
        ragreportagent.reset()
        internetagent.reset()

    # Create RetrieveAssistantAgent instance named "assistant"
    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
        },
    )

    # Create RetrieveUserProxyAgent instance named "ragreportagent" to read financial reports and answer questions
    ragreportagent = RetrieveUserProxyAgent(
        name="ragreportagent",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=3,
        retrieve_config={
            "task": "code",
            "docs_path": [],
            "custom_text_types": ["mdx"],
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
            "get_or_create": True,
        },
        code_execution_config=False,
    )

    # Create RetrieveUserProxyAgent instance named "ragreportagent" to google search and answer questions
    internetagent = RetrieveUserProxyAgent(
        name="internetagent",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=3,
        retrieve_config={
            "task": "code",
            "docs_path": [],
            "custom_text_types": ["mdx"],
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
            "get_or_create": True,
        },
        code_execution_config=False,
    )

    # Decide which logic to run based on user input
    user_input = input("Choose the agent to perform market analysis\n"
                       "1. RAG agent with existing PDF report\n"
                       "2. RAG agent with internet search ability\n\nPlease Enter 1 or 2:\n")

    valid_input = user_input in ("1", "2")
    while not valid_input:

        user_input = input("Please enter your choice (1 or 2): ")
        valid_input = user_input in ("1", "2")

        if not valid_input:
            print("Invalid input. Please enter a valid option.")

    # RAG search from report
    if user_input == "1":
        assistant.reset()
        ragreportagent.reset()
        qa_problem = input("Please enter the question: ")
        agent_report_search(ragreportagent)
        ragreportagent.initiate_chat(assistant, message=ragreportagent.message_generator, problem=qa_problem)

    # RAG search from google
    elif user_input == "2":
        assistant.reset()
        ragreportagent.reset()
        internetagent.reset()
        qa_problem = input("Please enter the question: ")
        agent_google_search(internetagent, qa_problem)
        internetagent.initiate_chat(assistant, message=internetagent.message_generator, problem=qa_problem)


if __name__ == "__main__":
    main()