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

config_list = autogen.config_list_from_json(env_or_file="../OAI_CONFIG_LIST")
SERP_API_KEY = os.getenv("SERP_API_KEY")
llm_config = {
    "timeout": 60,
    "temperature": 0,
    "config_list": config_list,
}
def add_data_resources(rag_agent, data_source):
    rag_agent._retrieve_config['docs_path'].append(data_source)


def agent_google_search(rag_agent, topic):
    retrieve_content = call_serpapi(topic)
    add_data_resources(rag_agent, os.path.join("../data", retrieve_content))

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
            filepath = os.path.join("data/google_results", filename)  # Update filepath to include the "data" directory
            with open(filepath, 'w') as file:
                json.dump(json_data, file, indent=4)
            print(f"Search results saved to {filepath}")
            return filepath
        else:
            print("Error: ", response.status_code)
    except requests.RequestException as e:
        print("Error: ", e)

def agent_report_search(rag_agent):
    for report in os.listdir('../data/report'):
        add_data_resources(rag_agent, os.path.join("../data/report", report))

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def main():
    # Receive user input

    boss = autogen.UserProxyAgent(
        name="Boss",
        is_termination_msg=termination_msg,
        human_input_mode="ALWAYS",
        code_execution_config=False,  # we don't want to execute code in this case.
        description="The boss who ask questions and give tasks.",
    )

    # Create RetrieveAssistantAgent instance named "assistant"
    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="ask internetagent for context if you do not have enough infomation",
        llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
        },
    )

    # Create RetrieveUserProxyAgent instance named "ragproxyagent"
    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
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
            "collection_name": "groupchat",
            "get_or_create": True,
        },
        code_execution_config=False,
        description="Assistant who has extra content retrieval pdf file for solving difficult problems.",
    )

    internetagent = RetrieveUserProxyAgent(
        name="internetagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        system_message="You are a extra content retrieval assistant, you are able to retrieval json file online for solving difficult problems.",
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

    def _reset_agents():
        boss.reset()
        assistant.reset()
        ragproxyagent.reset()
        internetagent.reset()

    def rag_chat():
        _reset_agents()
        groupchat = autogen.GroupChat(
            agents=[assistant, internetagent], messages=[], max_round=12, speaker_selection_method="round_robin"
        )
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        qa_problem = input("Please Enter The Question: ")
        agent_report_search(ragproxyagent)

        # Start chatting with boss_aid as this is the user proxy agent.
        ragproxyagent.initiate_chat(
            manager,
            message=ragproxyagent.message_generator,
            problem=qa_problem,
            n_results=3,
        )

    rag_chat()
main()