from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

client = InferenceClient()

response = client.text_generation("tell me a joke")

print(response)
