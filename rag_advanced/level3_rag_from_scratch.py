import os
from sentence_transformers import SentenceTransformer
from wikipediaapi import Wikipedia
import textwrap
import numpy as np
from groq import Groq
from dotenv import load_dotenv

def load_wikipedia_content(title):
    """Fetch and chunk content from Wikipedia"""
    wiki = Wikipedia('RAGBot/0.0', 'en')
    doc = wiki.page(title).text
    return doc.split('\n\n')  # Simple paragraph-based chunking

def print_paragraphs(paragraphs):
    """Print paragraphs with nice formatting"""
    for p in paragraphs:
        wrapped_text = textwrap.fill(p, width=100)
        print("-" * 65)
        print(wrapped_text)
        print("-" * 65)

def get_most_similar_paragraphs(query, paragraphs, model, top_k=3):
    """Find the most similar paragraphs to the query"""
    # Embed documents and query
    docs_embed = model.encode(paragraphs, normalize_embeddings=True)
    query_embed = model.encode(query, normalize_embeddings=True)
    
    # Calculate similarities
    similarities = np.dot(docs_embed, query_embed.T)
    
    # Get top k similar paragraphs
    top_k_idx = np.argsort(similarities, axis=0)[-top_k:][::-1].tolist()
    return [paragraphs[idx] for idx in top_k_idx]

def generate_answer(context, query, client):
    """Generate answer using Groq"""
    prompt = f"""
    You are a philoshoper and life coach. Use the following CONTEXT to answer the QUESTION at the end.

    CONTEXT: {context}
    QUESTION: {query}
    """
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    
    return response.choices[0].message.content

def main():
    load_dotenv()
    
    # Initialize the embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Initialize LLM client
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    # Define user query and data source
    query = "What was Studio Ghibli's first film?"
    wiki_page_title = "Hayao_Miyazaki"
    
    #Loading Data
    print(f"\nFetching Wikipedia content for: {wiki_page_title}")
    paragraphs = load_wikipedia_content(wiki_page_title)
    
    #Query
    print("\nFinding most relevant paragraphs...")
    most_similar_paragraphs = get_most_similar_paragraphs(query, paragraphs, model)
    
    print("\nMost relevant paragraphs:")
    print_paragraphs(most_similar_paragraphs)
    
    # Combine paragraphs into context
    context = "\n\n".join(most_similar_paragraphs)
    
    #Generation
    print("\nGenerating answer...")
    answer = generate_answer(context, query, client)
    
    print("\nAnswer:")
    print(answer)

if __name__ == "__main__":
    main()
