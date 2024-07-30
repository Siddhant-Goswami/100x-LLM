from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

# response = llm.invoke("Tell me a joke")
# print(response)

query = "Tell me a joke"

for chunks in llm.stream(query):
    print(chunks)