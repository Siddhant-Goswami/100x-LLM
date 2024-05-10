from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

# client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")
client = InferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1")

chat_completion = client.chat_completion(
    messages=[
        {
            "role": "user",
            "content": "Tell me a joke",
        }
    ], max_tokens=100)

print(chat_completion.choices[0].message.content)
