from openai import OpenAI
import base64
from pathlib import Path


class LLM():
    """
    Open AIに対して、APIコールを行う
    """
    def __init__(self, api_key):
        self.api_key =  api_key
 
    def build_prompt(self, prompt_user: str, prompt_system: str =None, image_encoded_list: list=None, image_description_list: list=None):
        """
        Input:
			prompt_system: システムプロンプト
			prompt_user: ユーザープロンプト
			image_encoded: 画像がbase64エンコーディングされたもの
		Output:
			prompt: (str) リスト形式のprompt
        """
	# ユーザプロンプトとシステムプロンプトから、promptを生成
        if not prompt_user:
            raise ValueError("prompt_userを入力してください")
        prompt = []
        if prompt_system:
            prompt.append({
                "role": "system",
                "content": prompt_system
            })

        user_content = []
        if image_encoded_list is None:
            image_encoded_list = []
        if image_description_list is None:
            image_description_list = []
            
        if len(image_encoded_list) != len(image_description_list):
            l = len(image_encoded_list) - len(image_description_list)
            if l > 0:
                image_description_list.extend(["NotFoud"] * l)
            elif l < 0:
                raise ValueError("リストの長さが違います")
        if image_encoded_list:
            for i in range(len(image_encoded_list)):
                user_content.append({
                    "type": "text",
                    "text": image_description_list[i]
                })
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                    "url": image_encoded_list[i]
                    }
                })
        
        user_content.append({
            "type": "text",
            "text": prompt_user
        })

        prompt.append({
            "role": "user",
            "content": user_content
        })

        return prompt

    def call(self, prompt: list):
        """
        Input:
            prompt: self.build_promptで生成されたprompt
        Output:
            response: (str) LLMの生成文章
        """
        client = OpenAI(
            api_key=self.api_key,
        )
        stream = client.chat.completions.create(
            model="o1", 
            messages=prompt, 
            stream=True
        )

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                # print(content, end="")
                response += content
        
        return response

    def gen(self, prompt_user: str="", prompt_system: str = None, image_encoded_list: list=None, image_description_list: list=None):

        prompt = self.build_prompt(prompt_user, prompt_system, image_encoded_list, image_description_list)
        response = self.call(prompt)
        return response
    

    def image_to_data_url(self,image_path):
         with open(image_path, "rb") as image_file:
            image_binary = image_file.read()
            base64_encoded = base64.b64encode(image_binary).decode('utf-8')
            file_extension = Path(image_path).suffix.lower()
            mime_type = {
				'.png': 'image/png',
				'.jpg': 'image/jpeg',
				'.jpeg': 'image/jpeg',
				'.gif': 'image/gif',
				'.bmp': 'image/bmp'
			}.get(file_extension, 'application/octet-stream')
            data_url= f"data:{mime_type};base64,{base64_encoded}"
            return data_url
