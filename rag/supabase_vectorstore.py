from llama_index.core import set_global_handler
from llama_index.core import SimpleDirectoryReader, Document, StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.supabase import SupabaseVectorStore
import textwrap
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")





documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

vector_store = SupabaseVectorStore(
    postgres_connection_string=(
        "postgresql://postgres.zeobrwrgwumqudubbplo:llamaindexRAG@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    ),
    collection_name="base_demo",
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

query_engine = index.as_query_engine()

response = query_engine.query("What did the author do growing up?")

print(textwrap.fill(str(response), 100))

