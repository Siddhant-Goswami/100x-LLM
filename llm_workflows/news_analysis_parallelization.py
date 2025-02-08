from utils import get_llm_response

def analyze_news_article(article_text: str):
    """
    Parallel processing example for news article analysis:
    1. Summarization
    2. Fact checking
    3. Sentiment analysis
    4. Key points extraction
    """
    
    print("Starting news article analysis...")
    
    # 1. Get a short summary
    print("Getting summary...")
    summary_prompt = f"Summarize this article in 2-3 sentences:\n{article_text}"
    summary = get_llm_response(summary_prompt)
    
    # 2. Extract key points
    print("Extracting key points...")
    points_prompt = f"List the 3 most important points from this article:\n{article_text}"
    key_points = get_llm_response(points_prompt)
    
    # 3. Check sentiment
    print("Analyzing sentiment...")
    sentiment_prompt = f"What is the overall sentiment of this article? Answer with: POSITIVE, NEGATIVE, or NEUTRAL:\n{article_text}"
    sentiment = get_llm_response(sentiment_prompt)
    
    # 4. Get different perspectives (voting pattern)
    print("Gathering different perspectives...")
    perspectives = []
    for i in range(3):
        perspective_prompt = f"Provide ONE unique perspective or takeaway from this article:\n{article_text}"
        perspective = get_llm_response(perspective_prompt)
        perspectives.append(perspective)
        print(f"Received perspective {i+1}")
    
    return {
        "summary": summary,
        "key_points": key_points,
        "sentiment": sentiment,
        "perspectives": perspectives
    }

def main():
    # Example news article
    article = """
    The rise of artificial intelligence has transformed various industries in recent years. 
    Companies are increasingly adopting AI solutions to automate tasks and improve efficiency. 
    While this has led to productivity gains, it has also raised concerns about job displacement. 
    However, experts suggest that AI will create new types of jobs while eliminating repetitive tasks. 
    Recent studies show that businesses using AI have seen a 25% increase in productivity. 
    Despite these benefits, there are ongoing debates about AI safety and ethics.
    """
    
    # Analyze the article
    results = analyze_news_article(article)
    
    # Print results
    print("\n=== Article Analysis Results ===")
    print("\nSummary:")
    print(results["summary"])
    
    print("\nKey Points:")
    print(results["key_points"])
    
    print("\nSentiment:")
    print(results["sentiment"])
    
    print("\nDifferent Perspectives:")
    for i, perspective in enumerate(results["perspectives"], 1):
        print(f"\nPerspective {i}:")
        print(perspective)

if __name__ == "__main__":
    main() 