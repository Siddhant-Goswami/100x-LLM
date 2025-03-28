import os
import json
import logging
from serpapi import GoogleSearch
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("react_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ReActAgent")

# Configure API keys
serpapi_key = os.environ.get("SERPER_API_KEY")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Global state to store memory and papers
memory = []
papers = []

def add_to_memory(entry_type, content):
    """Add an entry to the agent's memory"""
    memory.append({"type": entry_type, "content": content})
    logger.info(f"Added to memory: {entry_type} - {content[:100]}...")
    
def get_memory_as_text():
    """Convert memory to text format for LLM context"""
    memory_text = ""
    for entry in memory:
        prefix = "Thought: " if entry["type"] == "thought" else "Observation: "
        memory_text += f"{prefix}{entry['content']}\n\n"
    return memory_text

def reason(context):
    """Generate a reasoning trace based on current context"""
    logger.info("Generating reasoning trace...")
    prompt = f"""
    You are a research agent implementing the ReAct paradigm (Reasoning + Acting).
    Based on the current research context, generate a thoughtful reasoning trace that helps plan the next action.

    CURRENT CONTEXT:
    {context}

    Think step by step about what information you have, what you still need, and what would be the most useful next action.
    Thought:
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    thought = response.choices[0].message.content.strip()
    add_to_memory("thought", thought)
    return thought

def web_search(query):
    """Perform a web search using SerpAPI"""
    logger.info(f"Performing web search for: {query}")
    params = {
        "q": query,
        "api_key": serpapi_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if "organic_results" in results:
        top_results = results["organic_results"][:3]
        result_text = "\n\n".join([f"Title: {r['title']}\nSnippet: {r['snippet']}" 
                                  for r in top_results])
        add_to_memory("observation", f"Search results for '{query}':\n{result_text}")
        logger.info(f"Found {len(top_results)} results for query: {query}")
        return result_text
    else:
        add_to_memory("observation", f"No results found for '{query}'.")
        logger.warning(f"No results found for query: {query}")
        return "No results found."

def search_academic_papers(query):
    """Search for academic papers related to the query"""
    logger.info(f"Searching for academic papers on: {query}")
    academic_query = f"{query} research paper academic"
    results = web_search(academic_query)
    
    # Extract potential paper information
    paper_count_before = len(p)
    for line in results.split('\n'):
        if line.startswith("Title:") and ("paper" in line.lower() or "research" in line.lower()):
            paper_title = line.replace("Title:", "").strip()
            papers.append({"title": paper_title, "read": False})
    
    paper_list = "\n".join([f"- {p['title']}" for p in papers])
    add_to_memory("observation", f"Potential papers identified:\n{paper_list}")
    
    papers_found = len(papers) - paper_count_before
    logger.info(f"Identified {papers_found} new potential papers")
    return results

def summarize_paper(paper_idx):
    """Summarize a paper using the LLM"""
    logger.info(f"Attempting to summarize paper at index: {paper_idx}")
    # Convert paper_idx to integer if it's a string
    try:
        paper_idx = int(paper_idx)
    except (ValueError, TypeError):
        error_msg = f"Invalid paper index: {paper_idx} (must be a number)"
        add_to_memory("observation", error_msg)
        logger.error(error_msg)
        return "Invalid paper index."
    
    if paper_idx < 0 or paper_idx >= len(papers):
        error_msg = f"Invalid paper index: {paper_idx} (out of range)"
        add_to_memory("observation", error_msg)
        logger.error(error_msg)
        return "Invalid paper index."
    
    paper = papers[paper_idx]
    logger.info(f"Summarizing paper: {paper['title']}")
    
    # First, get content for the paper if it hasn't been read
    if not paper.get('read', False):
        logger.info(f"Paper not read yet, fetching content for: {paper['title']}")
        # Simulate paper content with a web search
        search_results = web_search(f"{paper['title']} abstract methodology results")
        paper['content'] = search_results
        paper['read'] = True
        add_to_memory("observation", f"Retrieved content for paper: {paper['title']}")
    
    prompt = f"""
    
    Summarize the following research paper content in a structured way:

    PAPER TITLE: {paper['title']}
    PAPER CONTENT: {paper.get('content', 'No content available')}

    Provide a concise summary covering the main objectives, methodology, and key findings:
    
    """

    logger.info("Generating paper summary...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    summary = response.choices[0].message.content.strip()
    paper['summary'] = summary
    add_to_memory("observation", f"Generated summary for paper: {paper['title']}")
    logger.info(f"Successfully summarized paper: {paper['title']}")
    return summary

def generate_research_report(topic):
    """Generate a research report on the topic"""
    logger.info(f"Generating research report on: {topic}")
    # Collect all paper summaries
    summaries = []
    for paper in papers:
        if 'summary' in paper:
            summaries.append(f"## {paper['title']}\n\n{paper['summary']}")
    
    all_summaries = "\n\n".join(summaries)
    logger.info(f"Including {len(summaries)} paper summaries in the report")
    
    prompt = f"""
    
    Create a comprehensive research report on the topic "{topic}" based on the following paper summaries:

    {all_summaries}

    Your report should include:
    1. Introduction to {topic}
    2. Key Findings from the Literature
    3. Conclusion

    FORMAT THE REPORT WITH MARKDOWN HEADINGS:
    
    """

    logger.info("Generating final research report...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    
    report = response.choices[0].message.content.strip()
    add_to_memory("observation", "Generated final research report")
    logger.info("Research report generated successfully")
    return report

def decide_next_action():
    """Decide the next action based on reasoning"""
    logger.info("Deciding next action...")
    context = get_memory_as_text()
    
    prompt = f"""
    
    You are a research agent implementing the ReAct paradigm (Reasoning + Acting).
    Based on the current research context, decide what action to take next.

    Available actions:
    1. search_academic_papers(query) - Search for academic papers
    2. summarize_paper(paper_idx) - Summarize a paper by its index (must be a number)
    3. generate_research_report(topic) - Generate a final research report

    CURRENT CONTEXT:
    {context}

    Based on the above context, what action should be taken next?
    
    Respond with a JSON object in the following format:
    {{
      "action": "action_name",
      "params": {{
        "param_name": "param_value"
      }}
    }}
    
    Where action_name must be one of: search_academic_papers, summarize_paper, or generate_research_report.
    For summarize_paper, the paper_idx parameter must be a number.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200,
        response_format={"type": "json_object"}
    )
    
    action_json = response.choices[0].message.content.strip()
    try:
        action_data = json.loads(action_json)
        action = action_data["action"]
        params = action_data.get("params", {})
        
        # Ensure paper_idx is an integer if the action is summarize_paper
        if action == "summarize_paper" and "paper_idx" in params:
            try:
                params["paper_idx"] = int(params["paper_idx"])
            except (ValueError, TypeError):
                error_msg = f"Invalid paper index: {params['paper_idx']} (must be a number)"
                add_to_memory("observation", error_msg)
                logger.warning(error_msg)
                # Default to the first paper if available
                params["paper_idx"] = 0 if papers else -1
        
        logger.info(f"Decided action: {action} with params: {params}")
        return action, params
    except Exception as e:
        error_msg = f"Error parsing action: {str(e)}"
        add_to_memory("observation", error_msg)
        logger.error(error_msg)
        # Default to search if parsing fails
        logger.info("Defaulting to search_academic_papers action")
        return "search_academic_papers", {"query": "AI Agents research"}

def research(topic, max_steps=3):
    """Main research function implementing the ReAct loop"""
    logger.info(f"Starting research on topic: {topic} with max_steps: {max_steps}")
    # Clear global state for new research
    global memory, papers
    memory = []
    papers = []
    
    add_to_memory("thought", f"Starting research on topic: {topic}")
    
    for step in range(max_steps):
        logger.info(f"Research step {step+1}/{max_steps}")
        # First, reason about the current state
        reason(get_memory_as_text())
        
        # Then, decide and execute the next action
        action, params = decide_next_action()
        
        if action == "search_academic_papers":
            search_academic_papers(params.get("query", topic))
        elif action == "summarize_paper":
            paper_idx = params.get("paper_idx", 0)
            # Ensure paper_idx is an integer
            if isinstance(paper_idx, str):
                try:
                    paper_idx = int(paper_idx)
                except ValueError:
                    logger.warning(f"Converting invalid paper_idx string '{paper_idx}' to 0")
                    paper_idx = 0
            summarize_paper(paper_idx)
        elif action == "generate_research_report":
            logger.info("Generating final report and ending research process")
            return generate_research_report(params.get("topic", topic))
    
    # If we've reached max steps, generate a report with what we have
    logger.info(f"Reached maximum steps ({max_steps}), generating final report")
    return generate_research_report(topic)

# Agent
topic = "Model Context Protocol"
    
print(f"Starting research on: {topic}")
print("This may take a few minutes...\n")
logger.info(f"Research process initiated on topic: {topic}")
    
report = research(topic)
    
print("\n=== RESEARCH REPORT ===\n")
print(report)
logger.info("Research report generated and displayed")
    
# Save the report to a file
with open("react_research_report.md", "w") as f:
    f.write(report)
    
print("\nReport saved to react_research_report.md")
logger.info("Research report saved to react_research_report.md")