import os
from huggingface_hub import InferenceClient
from huggingface_hub import InferenceApi
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(model="http://127.0.0.1:8080")

# hf_client = InferenceApi(repo_id="gpt-2", token=os.environ['HF_KEY']) 

generated_text = client.text_generation(prompt="Write a code for snake game")
print(generated_text)

# response = hf_client(text="The definition of machine learning inference is")

# print(response)

# 'model': "HuggingFaceH4/zephyr-7b-beta"