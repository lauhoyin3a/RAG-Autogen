import os
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv

data_path = os.path.join("data", "global-equity-views.pdf")

load_dotenv()

llm_config = {"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}
assistant = AssistantAgent("assistant", llm_config=llm_config)
user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

# Start the chat
user_proxy.initiate_chat(
    assistant,
    message="Tell me a joke about NVDA and TESLA stock prices.",
)