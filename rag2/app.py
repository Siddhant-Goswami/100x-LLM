import os
import requests
import numpy as np
from typing import List
import PyPDF2
from groq import Groq
import time

#######################################
# INITIAL SETUP
#######################################
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF using PyPDF2. 
    Returns the entire text as a single string.
    """
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Join text from all pages into one string
        return " ".join(page.extract_text() or "" for page in pdf_reader.pages)

def create_chunks(text: str, chunk_size: int = 500) -> List[str]:
    """
    Break the text into chunks of roughly chunk_size characters each. 
    This helps the embedding model handle smaller inputs.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_length += len(word) + 1  # +1 for space
        if current_length > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for a list of texts using a Hugging Face Inference API.
    This returns a list of numeric vectors.
    """
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/paraphrase-MiniLM-L6-v2"
    hf_headers = {
        "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    if not os.getenv('HF_TOKEN'):
        raise ValueError("HF_TOKEN environment variable is not set")
    
    embeddings = []
    batch_size = 8  # Process texts in smaller batches
    
    # Process texts in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            # Add delay to prevent overloading the API
            time.sleep(1)
            
            # Send the batch of texts
            response = requests.post(API_URL, headers=hf_headers, json={"inputs": batch})
            
            if response.status_code == 200:
                # Successful response
                batch_embeddings = response.json()
                embeddings.extend(batch_embeddings)
            else:
                print(f"Error response: {response.text}")
                # Try one by one if batch fails
                for text in batch:
                    time.sleep(1)
                    single_response = requests.post(API_URL, headers=hf_headers, json={"inputs": text})
                    if single_response.status_code == 200:
                        embeddings.append(single_response.json())
                    else:
                        print(f"Failed to get embedding for text: {text[:100]}...")
                        print(f"Error: {single_response.text}")
                        raise ValueError(f"API request failed with status {single_response.status_code}")
                
        except Exception as e:
            print(f"Error processing batch: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Response content: {response.text}")
            raise
            
    return embeddings

def search_relevant_chunks(query_embedding: List[float], 
                           chunk_embeddings: List[List[float]], 
                           chunks: List[str],
                           top_k: int = 3) -> List[str]:
    """
    Compute cosine similarity to find the top-k relevant chunks.
    """
    if not chunks or not chunk_embeddings:
        return []

    query_vec = np.array(query_embedding)
    chunk_mat = np.array(chunk_embeddings)
    
    similarities = np.dot(chunk_mat, query_vec) / (
        np.linalg.norm(chunk_mat, axis=1) * np.linalg.norm(query_vec)
    )
    
    # Sort by similarity in descending order
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

def answer_with_groq(context: str, question: str) -> str:
    """
    Send the context and question to the Groq LLM for an answer.
    """
    system_prompt = f"""Use the following context to answer the question. 
If you are not sure, say so.

Context:
{context}
"""
    # Groq chat completion
    response, _, _ = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        model="llama2-70b-4096",
    )
    return response

#######################################
# MAIN RAG WORKFLOW
#######################################
def main():
    """
    Demonstrates the entire RAG process:
      1. Extract text from a PDF
      2. Create chunks & compute embeddings
      3. Prompt user for a question
      4. Compute question embedding
      5. Retrieve relevant text chunks
      6. Get answer from Groq LLM
    """
    # Construct absolute path to the data file
    pdf_path = os.path.join(SCRIPT_DIR, "data", "paul_graham.txt")
    
    # 1. Read & chunk text
    with open(pdf_path, 'r') as f:
        text = f.read()
    chunks = create_chunks(text)
    # 2. Embed chunks
    chunk_embeddings = get_embeddings(chunks)
    
    # Interactive loop
    while True:
        user_question = input("Ask a question (type 'quit' to end): ")
        if user_question.lower() == "quit":
            break
        
        # 3. Compute question embedding
        question_embed = get_embeddings([user_question])[0]
        
        # 4. Find relevant chunks
        relevant_chunks = search_relevant_chunks(question_embed, chunk_embeddings, chunks, top_k=3)
        
        # 5. Prepare context (concatenate chunks)
        context_text = "\n\n".join(relevant_chunks)
        
        # 6. Get answer from LLM
        answer = answer_with_groq(context_text, user_question)
        
        print("\nAnswer:", answer, "\n")

if __name__ == "__main__":
    # Ensure you have your environment variables set:
    #   export GROQ_API_KEY=your_groq_api_key_here
    #   export HF_TOKEN=your_huggingface_token_here
    main()
