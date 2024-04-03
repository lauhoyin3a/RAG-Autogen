import json
import os
import re
import requests
from dotenv import load_dotenv
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.retrieve_utils import TEXT_FORMATS
import autogen
import chromadb

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
    google_search_url = get_google_search_url(topic, "google", SERP_API_KEY, "json")
    print(google_search_url)
    add_data_resources(rag_agent, google_search_url)

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
            with open(filename, 'w') as file:
                json.dump(json_data, file, indent=4)
            print(f"Search results saved to {filename}")
            return filename
        else:
            print("Error: ", response.status_code)
    except requests.RequestException as e:
        print("Error: ", e)

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

# Add data sources to the RetrieveUserProxyAgent
qa_problem = "What's your overall recommendation related to global equity strategies?"
retrieve_content = call_serpapi(qa_problem)
ragproxyagent._retrieve_config['docs_path'].append(os.path.join('data', retrieve_content))

# Reset the assistant before starting a new conversation
assistant.reset()

# Initiate the chat between the assistant and the user proxy agent
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=qa_problem)