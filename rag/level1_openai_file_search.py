from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(); client = OpenAI()

vs_id = "vs_68fca6e7bdd081918701b37b762420aa"

def ask(q):
    r = client.responses.create(
        input=q, model="gpt-4o-mini",
        tools=[{"type": "file_search", "vector_store_ids":[vs_id]}]
    )
    return r.output[-1].content[0].text

print(ask("Will i learn RAG?"))
