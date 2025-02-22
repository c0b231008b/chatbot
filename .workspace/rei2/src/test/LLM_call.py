import sys
import os
import yaml
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'LLM')))
from LLM import LLM  
from server import rei  

with open('/root/.workspace/rei2/src/config/config.yaml', 'r') as rf:  
    config = yaml.safe_load(rf)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server')))

a = rei(api_key=config["OPENAI_API_KEY"])
b = a.execute("好きな食べ物は？")
data = json.loads(b)
print(data["output"])