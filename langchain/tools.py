import os
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

@tool
def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b."""
    return a * b


tools = [add, multiply]


llm = ChatGroq(model="llama3-8b-8192")


llm_with_tools = llm.bind_tools(tools)
llm_forced_to_multiply = llm.bind_tools(tools, tool_choice="auto")  # Changed from "any" to "auto"
response = llm_forced_to_multiply.invoke("what is 2 + 4")
print(response)
