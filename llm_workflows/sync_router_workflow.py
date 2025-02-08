from utils import get_llm_response

def customer_service_router_simple(query: str):
    """Simplified example of routing customer service queries"""
    
    # Determine query type
    router_prompt = f"""Classify this query into one of these categories:
    1. Refund Request
    2. Technical Support
    3. Product Information
    Return only the category number."""
    
    category = get_llm_response(router_prompt).strip()
    
    # Route to appropriate handler
    handlers = {
        "1": "You are handling a refund request. Be empathetic: ",
        "2": "You are providing technical support. Be clear and precise: ",
        "3": "You are sharing product information. Be informative: "
    }
    
    prompt = handlers.get(category, handlers["3"]) + query
    response = get_llm_response(prompt)
    
    return category, response

def main():
    # Test queries
    queries = [
        "I want a refund for my broken product",
        "How do I reset my password?",
        "What features come with the premium plan?"
    ]
    
    # Process each query
    for query in queries:
        print(f"\nCustomer Query: {query}")
        category, response = customer_service_router_simple(query)
        print(f"Category: {category}")
        print(f"Response: {response}")

if __name__ == "__main__":
    main() 