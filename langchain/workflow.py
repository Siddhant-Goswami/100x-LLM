from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

# components
model = ChatGroq(model="llama3-8b-8192")
parser = StrOutputParser()

messages = [
    SystemMessage(content="Translate the following from English into Italian"),
    HumanMessage(content="hi!"),
]

chain = model | parser 

parsed_message = chain.invoke(messages)
print(parsed_message)



