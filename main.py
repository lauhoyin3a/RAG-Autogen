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

def get_google_search_url(topic, engine, api_key, output_format):
    serp_url = "https://serpapi.com/search"
    search_url = f"{serp_url}?q={topic}&engine={engine}&api_key={api_key}&output={output_format}"
    return search_url

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
            filepath = os.path.join("data", filename)  # Update filepath to include the "data" directory
            with open(filepath, 'w') as file:
                json.dump(json_data, file, indent=4)
            print(f"Search results saved to {filepath}")
            return filepath
        else:
            print("Error: ", response.status_code)
    except requests.RequestException as e:
        print("Error: ", e)

def run_file(filename):
    # Run the Python file based on the user input
    exec(open(filename).read())

def main():
    # Receive user input
    user_input = input("Choose the agent to perform market analysis\n1. RAG agent with existing PDF report\n2. RAG agent with internet search ability\n\nPlease Enter 1 or 2:\n")

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

    # Create RetrieveUserProxyAgent instance named "ragproxyagent"
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
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

    internetagent = RetrieveUserProxyAgent(
        name="internetagent",
        human_input_mode="NEVER",
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
    if user_input == "1":
        assistant.reset()
        ragproxyagent.reset()
        qa_problem = input("Please Enter The Question: ")
        ragproxyagent._retrieve_config['docs_path'].append(os.path.join("data", "2024-03-25-JPMorgan-Equity Strategy Equity PE multiples in historical context - earnings vs...-107204257.pdf"))
        ragproxyagent._retrieve_config['docs_path'].append(os.path.join("data", "2024-03-25-Morgan Stanley-Asia Quantitative Strategy Biweekly Perspectives Rising Signs Of Marke...-107204434.pdf"))
        ragproxyagent._retrieve_config['docs_path'].append(os.path.join("data", "2024-03-25-Morgan Stanley-US Equity Strategy Weekly Warm-up Great Expectations Suggest More Rota...-107204697.pdf"))

        print(ragproxyagent._retrieve_config)
        ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=qa_problem)

    elif user_input == "2":
        assistant.reset()
        ragproxyagent.reset()
        internetagent.reset()
        qa_problem = input("Please Enter The Question: ")
        agent_google_search(internetagent, qa_problem)

        internetagent.initiate_chat(assistant, message=internetagent.message_generator, problem=qa_problem)

    else:
        print("Invalid input. Please enter a valid option.")

if __name__ == "__main__":
    main()