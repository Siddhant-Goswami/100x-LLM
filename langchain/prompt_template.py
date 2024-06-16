from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()

# components: parser, model, prompt_template
parser = StrOutputParser()

model_1 = ChatGroq(model="llama3-8b-8192", temperature=0.5)

model_2 = ChatGroq(model="llama3-8b-8192", temperature=1)

system_template = "Translate the following into {language}:"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

chain = prompt_template | model_1 | model_2 | parser 


message = chain.invoke({"language": "italian", "text": "hi"})






