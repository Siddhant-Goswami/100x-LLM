import os
from sentence_transformers import SentenceTransformer
from wikipediaapi import Wikipedia
import textwrap
import numpy as np
from openai import OpenAI
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
    """Generate answer using OpenAI"""
    prompt = f"""
    Use the following CONTEXT to answer the QUESTION at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    CONTEXT: {context}
    QUESTION: {query}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # You can change this to gpt-4 if needed
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    
    return response.choices[0].message.content

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("Alibaba-NLP/gte-base-en-v1.5", trust_remote_code=True)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Example query and Wikipedia page
    query = "What was Studio Ghibli's first film?"
    wiki_title = "Hayao_Miyazaki"
    
    print(f"\nFetching Wikipedia content for: {wiki_title}")
    paragraphs = load_wikipedia_content(wiki_title)
    
    print("\nFinding most relevant paragraphs...")
    most_similar_paragraphs = get_most_similar_paragraphs(query, paragraphs, model)
    
    print("\nMost relevant paragraphs:")
    print_paragraphs(most_similar_paragraphs)
    
    # Combine paragraphs into context
    context = "\n\n".join(most_similar_paragraphs)
    
    print("\nGenerating answer...")
    answer = generate_answer(context, query, client)
    
    print("\nAnswer:")
    print(answer)

if __name__ == "__main__":
    main()
