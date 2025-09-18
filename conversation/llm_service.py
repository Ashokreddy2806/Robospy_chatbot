# to get llm wrapper to work it needs to be cloned installed from here: pip install git+https://github.com/OFAI/python-llms-wrapper.git, but is included in requirements.txt
# there seems to be an issue on german windows in python 3.13.3 with encoding in the dependency "litellm"
# therefore uninstall "litellm" from your virutal environment and clone this specific branch: git clone --branch issue10272 https://github.com/johann-petrak/litellm.git
# cd into the folder and use 'pip install .' to install the new, cloned branch of "litellm" 
from openai import OpenAI
import os, sys
from dotenv import load_dotenv
from typing import Optional, List, Dict
sys.path.append(os.path.join(".."))
from llms_wrapper.llms import LLMS, toolnames2funcs, get_func_by_name
from llms_wrapper.config import update_llm_config


load_dotenv()

# Instructions for LLM-Wrapper: https://github.com/OFAI/python-llms-wrapper/blob/main/notebooks/test-streaming.ipynb
def complete(messages, model="openai/gpt-4o"):
    print("WORKS!")
    config = dict(
        llms=[
            dict(llm="openai/gpt-4o"),
            dict(llm="openai/gpt-4o-mini"),
            dict(llm="mistral/mistral-large-latest"), # needs subscription
            dict(llm="anthropic/claude-3-7-sonnet-20250219"),
            dict(llm="deepseek/deepseek-chat"),
            dict(llm="groq/llama3.1-8b", api_url="http://192.168.50.31:8080"), # locally version of LLAMA
        ],
        providers=dict(
            openai=dict(api_key_env=("OPENAI_API_KEY")), # works, got subscription
            mistral=dict(api_key_env=("MISTRAL_API_KEY")), # works, not sure if token limit will be reached
            anthropic=dict(api_key_env=("ANTHROPIC_API_KEY")),# does not work!
            deepseek=dict(api_key_env=("DEEPSEEK_API_KEY")), # needs a balance at endpoint, tried 5€
            groq=dict(api_key_env=("LLAMA_LOCAL_API_KEY")) # works when hosted locally
        )
    )
    config = update_llm_config(config)
    llms = LLMS(config)
    llms.list_aliases()

    ret = llms.query(model, messages, temperature=0.5, max_tokens=1000, stream=True)

    if ret["ok"]:
        for chunk in ret["chunks"]:
            if chunk["error"]:
                print()
                print("Error:", chunk["error"])
                break
            print(chunk["answer"], end="")
            yield chunk["answer"]
        print()
    else:
        print("Error:", ret["error"])
