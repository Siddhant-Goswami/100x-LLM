from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

#log data
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# load data
documents = SimpleDirectoryReader("data").load_data()

# Create an Index
# Chunk data and convert it into vector embeddings
index = VectorStoreIndex.from_documents(documents)

# Create a QueryEngine for Retrieval & Augmentation
query_engine = index.as_query_engine()

# Generate response by asking a query to the QueryEngine
response = query_engine.query("What is the first program author tried?")

print(response)