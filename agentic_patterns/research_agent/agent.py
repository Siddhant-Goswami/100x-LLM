from serpapi import GoogleSearch
import os

serpapi_key = os.environ.get("SERPER_API_KEY")

def web_search(query):
    """
    Performs a web search using SerpAPI.
    
    :param query: The search query
    :return: A string containing the top search results
    """
    # Set up the parameters for the SerpAPI search
    params = {
        "q": query,
        "api_key": serpapi_key
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # Extract and format the top 3 results
    if "organic_results" in results:
        top_results = results["organic_results"][:3]
        return "\n\n".join([f"Title: {r['title']}\nSnippet: {r['snippet']}" for r in top_results])
    else:
        return "No results found."

# Input: Topic
topic = "ReAct"

def react_agent(topic: str):
    # 1. Research the topic - Google Search
    search_results = web_search(topic)
    # 2. Find the most relevant papers
    # 3. Read the papers
    # 4. Summarize the papers
    # 5. Write a research report
    return search_results

# Agent
report = react_agent(topic)

# Output: Research report
print(report)


