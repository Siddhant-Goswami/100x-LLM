import os
from groq import Groq

# Initialize Groq client - make sure to set your GROQ_API_KEY environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_llm_response(prompt: str, model: str = "deepseek-r1-distill-llama-70b"):
    """Simple synchronous helper function to get response from LLM"""
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model
    )
    return completion.choices[0].message.content

async def get_llm_response_async(prompt: str, model: str = "deepseek-r1-distill-llama-70b"):
    """Simple asynchronous helper function to get response from LLM"""
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model
    )
    return completion.choices[0].message.content 
