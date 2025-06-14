from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(); client = OpenAI()

vs_id = "YOUR_VECTOR_STORE_ID"

def ask(q):
    r = client.responses.create(
        input=q, model="gpt-4o-mini",
        tools=[{"type": "file_search", "vector_store_ids":[vs_id]}]
    )
    return r.output[-1].content[0].text

print(ask("when will i learn to automate my job in this program?"))
