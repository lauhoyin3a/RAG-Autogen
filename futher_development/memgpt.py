from memgpt.autogen.memgpt_agent import create_memgpt_autogen_agent_from_config

# create a config for the MemGPT AutoGen agent
config_list_memgpt = [
    {
        "model": "gpt-4",
        "context_window": 8192,
        "preset": "memgpt_chat",  # NOTE: you can change the preset here
        # OpenAI specific
        "model_endpoint_type": "openai",
        "openai_key": os.getenv("OPENAI_API_KEY"),
    },
]
llm_config_memgpt = {"config_list": config_list_memgpt, "seed": 42}

# there are some additional options to do with how you want the interface to look (more info below)
interface_kwargs = {
    "debug": False,
    "show_inner_thoughts": True,
    "show_function_outputs": False,
}

# then pass the config to the constructor
memgpt_autogen_agent = create_memgpt_autogen_agent_from_config(
    "MemGPT_agent",
    llm_config=llm_config_memgpt,
    interface_kwargs=interface_kwargs,
    skip_verify=True,
    auto_save=False,
)