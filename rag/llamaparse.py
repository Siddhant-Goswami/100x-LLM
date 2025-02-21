from llama_parse import LlamaParse  # pip install llama-parse
from llama_index.core import SimpleDirectoryReader  # pip install llama-index
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from dotenv import load_dotenv
import os

load_dotenv()

# Create data directory if it doesn't exist
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Created directory: {data_dir}")
    print("Please add your PDF files to the data directory before running this script")
    exit(0)

# Check if directory is empty
if len(os.listdir(data_dir)) == 0:
    print("The data directory is empty. Please add PDF files before running this script")
    exit(0)

# Embedding model
embed_model=OpenAIEmbedding(model="text-embedding-3-small")
llm = OpenAI(model="gpt-4o-mini")
Settings.llm = llm


# Parse docs into markdown
parser = LlamaParse(result_type="markdown")

# Read pdf files from data dir
reader = SimpleDirectoryReader(input_dir="./data", file_extractor={".pdf": parser})

# Load the doc
documents = reader.load_data()
# print(documents[0].text[0:1000])

# Use MENP to convert the markdown into a set of table and text node.
node_parser = MarkdownElementNodeParser(llm=OpenAI(model="gpt-4o-mini"), num_workers=8)

nodes = node_parser.get_nodes_from_documents(documents)

base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

recursive_index = VectorStoreIndex(nodes=base_nodes+objects)

query_engine = recursive_index.as_query_engine(similarity_top_k=25)

# query_1 = "My trip was delayed and I paid 45, how much am I covered for?"

# response_1 = query_engine.query(query_1)
# print(str(response_1))


documents_with_instruction_parser = LlamaParse(result_type="markdown", parsing_instruction="""
This document is an insurance policy.
When a benefit/coverage/exlusion is described in the document append a line of the following benefits string format (where coverage could be an exclusion).

For {nameofrisk} and in this condition {whenDoesThecoverageApply} the coverage is {coverageDescription}.

If the document contains a benefits TABLE that describe coverage amounts, do not ouput it as a table, but instead as a list of benefits strings.

""")

reader_with_instruction = SimpleDirectoryReader(input_dir="./data", file_extractor={".pdf": documents_with_instruction_parser})
documents_with_instruction = reader_with_instruction.load_data()

target_page = 45
pages_vanilla = documents[0].text.split("\n---\n")
pages_with_instructions = documents_with_instruction[0].text.split("\n---\n")

print(pages_vanilla[target_page])
print("\n\n=========================================================\n\n")
print(pages_with_instructions[target_page])