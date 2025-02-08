from utils import get_llm_response

def code_review_simple(code_snippet: str):
    """Simplified example of parallel processing concept for code review"""
    
    # Define different aspects to review
    analysis_aspects = [
        "Check for security vulnerabilities",
        "Review code style and best practices",
        "Analyze performance implications"
    ]
    
    # Get reviews for each aspect
    reviews = []
    print("Starting code analysis...")
    for aspect in analysis_aspects:
        prompt = f"Review this code focusing on {aspect}:\n{code_snippet}"
        review = get_llm_response(prompt)
        reviews.append(review)
        print(f"Completed review for: {aspect}")
    
    # Get votes on implementation
    votes = []
    print("\nGathering improvement suggestions...")
    for i in range(3):  # Get 3 different opinions
        prompt = f"Suggest ONE improvement for this code:\n{code_snippet}"
        vote = get_llm_response(prompt)
        votes.append(vote)
        print(f"Received suggestion {i+1}")
    
    return {
        "reviews": list(zip(analysis_aspects, reviews)),
        "improvement_suggestions": votes
    }

def main():
    # Example code to review
    code_snippet = """
    def process_user_input(user_input):
        # Remove spaces and convert to lowercase
        cleaned_input = user_input.strip().lower()
        
        # Basic validation
        if len(cleaned_input) == 0:
            return None
            
        # Process the input
        result = cleaned_input.split(',')
        return [item for item in result if item]
    """
    
    # Run the code review
    results = code_review_simple(code_snippet)
    
    # Print results
    print("\nCode Review Results:")
    for aspect, review in results["reviews"]:
        print(f"\n{aspect}:")
        print(review)
    
    print("\nImprovement Suggestions:")
    for i, suggestion in enumerate(results["improvement_suggestions"], 1):
        print(f"\nSuggestion {i}:")
        print(suggestion)

if __name__ == "__main__":
    main() 