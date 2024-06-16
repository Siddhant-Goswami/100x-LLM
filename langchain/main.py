from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
load_dotenv()

parser = StrOutputParser()

model = ChatGroq(model="llama3-8b-8192")

messages = [
    SystemMessage(content="Translate the following from English into Italian"),
    HumanMessage(content="hi!"),
]

chain = model | parser

message = chain.invoke(messages)

print(message)



