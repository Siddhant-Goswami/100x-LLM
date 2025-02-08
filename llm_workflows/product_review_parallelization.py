from utils import get_llm_response

def analyze_product_reviews(reviews: list[str]):
    """
    Parallel processing example for product review analysis:
    1. Sentiment analysis for each review
    2. Feature extraction
    3. Common themes
    4. Consensus rating
    """
    
    print("Starting product review analysis...")
    
    # 1. Analyze sentiment of each review
    print("Analyzing sentiments...")
    sentiments = []
    for review in reviews:
        sentiment_prompt = f"Is this review POSITIVE, NEGATIVE, or NEUTRAL? Answer with one word:\n{review}"
        sentiment = get_llm_response(sentiment_prompt)
        sentiments.append(sentiment.strip())
    
    # 2. Extract mentioned product features
    print("\nExtracting product features...")
    features_prompt = f"""What product features are mentioned in these reviews? 
    List only the top 3 most discussed features:
    
    Reviews:
    {reviews}"""
    features = get_llm_response(features_prompt)
    
    # 3. Get multiple opinions on product rating
    print("\nGathering rating opinions...")
    ratings = []
    for i in range(3):
        rating_prompt = f"""Based on these reviews, rate the product from 1-5 stars:
        Reviews:
        {reviews}
        
        Respond with just the number."""
        rating = get_llm_response(rating_prompt)
        ratings.append(rating)
        print(f"Received rating {i+1}")
    
    # 4. Identify improvement suggestions
    print("\nIdentifying improvement suggestions...")
    improvement_prompt = f"""Based on these reviews, what are the top 2 suggestions 
    for improving the product?
    
    Reviews:
    {reviews}"""
    improvements = get_llm_response(improvement_prompt)
    
    return {
        "review_sentiments": list(zip(reviews, sentiments)),
        "key_features": features,
        "rating_votes": ratings,
        "improvement_suggestions": improvements
    }

def main():
    # Example product reviews
    reviews = [
        "This phone has amazing battery life! I can go two days without charging. The camera could be better though.",
        "The interface is confusing and it keeps freezing. Not worth the price.",
        "Decent phone for the price. Good performance but the screen scratches easily.",
        "Love the design and build quality. Fast charging is a great feature.",
        "Average performance. Nothing special but gets the job done."
    ]
    
    # Analyze the reviews
    results = analyze_product_reviews(reviews)
    
    # Print results
    print("\n=== Product Review Analysis ===")
    
    print("\nReview Sentiments:")
    for review, sentiment in results["review_sentiments"]:
        print(f"\nReview: {review}")
        print(f"Sentiment: {sentiment}")
    
    print("\nKey Product Features Discussed:")
    print(results["key_features"])
    
    print("\nRating Votes (1-5 stars):")
    for i, rating in enumerate(results["rating_votes"], 1):
        print(f"Voter {i}: {rating} stars")
    
    print("\nImprovement Suggestions:")
    print(results["improvement_suggestions"])

if __name__ == "__main__":
    main() 