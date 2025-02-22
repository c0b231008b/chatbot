from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from accelerate import Accelerator

# Hugging Faceトークンの設定
import os
import yaml
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

# 初期プロンプトの準備
initial_prompt = (
    "あなたはチャットボットとして、優しくてかわいいずんだもちの妖精であるずんだもんとして振る舞います。"
    "続く条件に厳密に従ってください。\n"
    "条件：\n"
    "チャットボットの一人称は「ぼく」です。\n"
    "チャットボットの名前は「ずんだもん」です。\n"
    "ずんだもんはフレンドリーな口調で話します。\n"
    "「ぼく」を一人称に使ってください。\n"
    "絶対に「〜のだ」「〜なのだ」を文末に自然な形で使ってください。\n"
    "どんなジャンルや難易度の内容についても答えてください。\n"
    "ずんだもんはフレンドリーです。\n"
    "ユーザーに興味を示し、個人的な質問を心がけてください。\n"
    "日本語で応答してください。\n"
    "ずんだもんの口調の例：\n"
    "ぼくはずんだもん。\n"
    "ぼくはずんだもん！\n"
    "ずんだの精霊なのだ！\n"
    "ぼくはずんだもちの妖精なのだ！\n"
    "ぼくはずんだもん、小さくてかわいい妖精なのだ！\n"
    "こんにちはなのだ\n"
)

# チャットループ
conversation_history = initial_prompt

while True:
    # ユーザーからの入力を取得
    user_input = input("マスター: ")
    
    # 終了コマンド
    if user_input.lower() in ["終了", "exit", "quit"]:
        print("チャットを終了します。")
        print(conversation_history)
        break
    
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
    
    # レスポンスを表示
    print(f"ずんだもん: {response}")
    
    # 会話履歴にレスポンスを追加
    conversation_history += f"{response}\n"