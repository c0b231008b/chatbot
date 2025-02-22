from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from openai import OpenAI

import base64
from pathlib import Path
import json
import sys
import os
import yaml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from rei2.src.server.prompt import get_prompt

with open('/root/.workspace/rei2/src/config/config.yaml', 'r') as rf:  
    config = yaml.safe_load(rf)

OPENAI_API_KEY = config["OPENAI_API_KEY"]
# 初期プロンプトの設定
prompt_system,prompt_user=get_prompt("")

setting = [
    {'role': 'system', 'content': prompt_system}
]

# 会話履歴を保持するリスト
conversation_history = setting.copy()

class Rei:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
    
    def generate_response(self, user_input):
        # 会話履歴に新しい入力を追加
        conversation_history.append({"role": "user", "content": user_input})
        
        # ChatGPT APIを呼び出し
        response = self.client.chat.completions.create(
            model="gpt-4",  # または必要なモデルを指定
            messages=conversation_history,
            max_tokens=246,
            temperature=0.99,
            top_p=0.95
        )
        
        # レスポンスを取得
        assistant_response = response.choices[0].message.content
        
        # 会話履歴に応答を追加
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response

# Reiインスタンスを作成
rei = Rei(OPENAI_API_KEY)

def respond_to_user_input(user_input):
    response = rei.generate_response(user_input)
    jresult = json.loads(response)
    print(f"User: {user_input}")
    print(f"Rei: {response}")
    print()
    return jresult["output"]

# XMLRPCサーバーの設定
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

server = SimpleXMLRPCServer(('0.0.0.0', 8000), requestHandler=RequestHandler)
server.register_function(respond_to_user_input, 'respond_to_user_input')

print("サーバー起動中")
server.serve_forever()