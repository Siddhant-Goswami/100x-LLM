import asyncio
from utils import get_llm_response

async def customer_service_router(query: str):
    """Example of routing customer service queries to specialized handlers"""
    
    # Classification prompt to determine query type
    router_prompt = f"""Classify this customer service query into one of these categories:
    1. Refund Request
    2. Technical Support
    3. Product Information
    4. Account Management
    5. Billing Issue
    
    Query: {query}
    Return only the category number."""
    
    # Get classification
    category = (await get_llm_response(router_prompt)).strip()
    
    # Route to specialized handlers with appropriate tone and expertise
    handlers = {
        "1": """You are a customer service representative handling refunds.
               Be empathetic and solution-oriented.
               Query to handle: """,
        "2": """You are a technical support specialist.
               Provide clear, step-by-step solutions.
               Query to handle: """,
        "3": """You are a product information specialist.
               Be informative and highlight key features.
               Query to handle: """,
        "4": """You are an account management specialist.
               Be security-conscious and thorough.
               Query to handle: """,
        "5": """You are a billing specialist.
               Be precise and detail-oriented.
               Query to handle: """
    }
    
    prompt_prefix = handlers.get(category, handlers["3"])
    response = await get_llm_response(prompt_prefix + query)
    
    return category, response

async def complexity_based_router(query: str):
    """Example of routing queries based on complexity to optimize cost and performance"""
    
    # Analyze query complexity
    complexity_prompt = f"""Analyze this query's complexity based on:
    1. Technical depth required
    2. Context needed
    3. Reasoning steps required
    4. Domain expertise needed
    
    Query: {query}
    
    Rate complexity from 1-5 (1=simple, 5=very complex).
    Return only the number."""
    
    # Get complexity rating
    complexity = int((await get_llm_response(complexity_prompt)).strip())
    
    # Route based on complexity
    if complexity <= 2:
        model = "mixtral-8x7b-32768"  # Use faster/cheaper model for simple queries
        prompt_prefix = "Provide a straightforward answer: "
    else:
        model = "mixtral-8x7b-32768"  # Use more powerful model for complex queries
        prompt_prefix = """Break this down step by step and provide a detailed explanation.
                          Consider multiple aspects and provide examples.
                          Query: """
    
    response = await get_llm_response(prompt_prefix + query, model=model)
    
    return complexity, model, response

# Example usage
async def main():
    # Example 1: Customer Service Routing
    print("Example 1: Customer Service Query Routing")
    queries = [
        "I want a refund for my recent purchase that arrived damaged",
        "How do I reset my account password?",
        "Can you explain the features of your premium plan?",
        "My last bill seems incorrect, can you check it?",
        "The app keeps crashing when I try to upload photos"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        category, response = await customer_service_router(query)
        print(f"Routed to Category: {category}")
        print(f"Response: {response}")
    
    # Example 2: Complexity-Based Routing
    print("\n\nExample 2: Complexity-Based Query Routing")
    queries = [
        "What's the weather like today?",
        "How do I sort a list in Python?",
        "Explain quantum entanglement and its implications for quantum computing",
        "What's the difference between REST and GraphQL?",
        "Explain the architectural implications of microservices vs monolithic systems"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        complexity, model, response = await complexity_based_router(query)
        print(f"Complexity Level: {complexity}")
        print(f"Routed to Model: {model}")
        print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main()) 