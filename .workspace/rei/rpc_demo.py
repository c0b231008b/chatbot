from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from accelerate import Accelerator
import os
import yaml

# Hugging Faceトークンの設定
with open('/root/.workspace/rei2/src/config/config.yaml', 'r') as rf:  
    config = yaml.safe_load(rf)
HF_TOKEN = config["HF_TOKEN"]

# accelerateライブラリのアクセラレータを初期化
accelerator = Accelerator()

# トークナイザーとモデルの準備
tokenizer = AutoTokenizer.from_pretrained(
    "tokyotech-llm/Swallow-MS-7b-v0.1",
    use_auth_token=HF_TOKEN
)
# パディングトークンを設定
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    "tokyotech-llm/Swallow-MS-7b-v0.1",
    torch_dtype=torch.float16,
    device_map="auto",
    use_auth_token=HF_TOKEN
)

# モデルとトークナイザーをアクセラレータで準備
model, tokenizer = accelerator.prepare(model, tokenizer)

# グローバル変数として会話履歴を初期化
conversation_history = ""

# サーバーによって呼び出される関数
def respond_to_user_input(user_input):
    global conversation_history

    # 入力を会話履歴に追加
    conversation_history += f"マスター: {user_input}\nずんだもん:"

    # 推論の実行
    inputs = tokenizer(conversation_history, return_tensors="pt", padding=True)
    input_ids = inputs.input_ids.to(accelerator.device)
    attention_mask = inputs.attention_mask.to(accelerator.device)
    
    tokens = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=128,
        temperature=0.99,
        top_p=0.95,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
    )
    response = tokenizer.decode(tokens[0], skip_special_tokens=True)

    # レスポンスのフォーマットを調整
    response = response[len(conversation_history):].strip().split("\n")[0]

    # 会話履歴にレスポンスを追加
    conversation_history += f"{response}\n"

    return response

# サーバーの設定と起動
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

server = SimpleXMLRPCServer(('127.0.0.1', 8000), requestHandler=RequestHandler)
server.register_function(respond_to_user_input, 'respond_to_user_input')

print("サーバーを起動しています")
server.serve_forever()