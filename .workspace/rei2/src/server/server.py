from openai import OpenAI
import base64
from pathlib import Path
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'LLM')))
from LLM import LLM  

from prompt import get_prompt
# prompt_system, prompt_user = get_prompt("element")
# print(prompt_system)

class rei():
    def __init__(self, api_key):
        self.llm = LLM(api_key=api_key)
    
    def execute(self, element: str):
        prompt_system,prompt_user=get_prompt(element)
        response = self.llm.gen(
            prompt_system=prompt_system,
            prompt_user=prompt_user,
        )
        return response
    

