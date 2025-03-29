import os
import json
from groq import Groq
from serpapi import GoogleSearch

def research_agent(topic, max_iterations=3):
    """
    Research agent using an LLM for thought generation and research actions.
    
    :param topic: The research topic to investigate
    :param max_iterations: Maximum number of iterations to prevent infinite loops
    :return: The final research report or a message indicating incomplete research
    """
    memory = ""
    papers_data = []  # Store papers data for final report
    
    for i in range(max_iterations):
        try:
            # Generate a thought and decide on an action using LLM
            thought, action, action_input = generate_thought_and_action(topic, memory)
            
            # Print the current iteration's details
            print(f"Iteration {i+1}:")
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            print(f"Action Input: {action_input}")

            # Perform the chosen action and get the observation
            observation = perform_action(action, action_input)
            print(f"Observation: {observation}")
            print("---")

            # Store papers data if we're searching
            if action == "search_academic_papers":
                try:
                    papers_data = json.loads(observation)
                except:
                    papers_data = []

            # Update the memory with the current iteration's information
            # Only keep the last iteration in memory to prevent token overflow
            memory = f"Thought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"

            # If we have papers and haven't summarized yet, move to summarize
            if action == "search_academic_papers" and papers_data:
                thought = "Found papers. Now summarizing them."
                action = "summarize_paper"
                action_input = json.dumps(papers_data)
                observation = perform_action(action, action_input)
                memory = f"Thought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"
                
                # Generate final report after summarization
                thought = "Papers summarized. Generating final report."
                action = "generate_research_report"
                action_input = observation
                observation = perform_action(action, action_input)
                return observation

        except Exception as e:
            print(f"Error in iteration {i+1}: {str(e)}")
            continue

    return "Research could not be completed within the given number of iterations."

def generate_thought_and_action(topic, memory):
    """
    Uses an LLM to generate research thoughts and actions.
    
    :param topic: The research topic
    :param memory: Current research memory/context
    :return: thought, action, action_input
    """
    # Construct a more concise prompt for the AI model
    prompt = f"""Research Topic: {topic}

Previous Actions:
{memory}

Next Action (choose one):
1. search_academic_papers - Find academic papers
2. summarize_paper - Summarize papers
3. generate_research_report - Create final report

Format:
Thought: [reasoning]
Action: [action_name]
Action Input: [specific input]"""

    # Define the available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_academic_papers",
                "description": "Search for academic papers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "summarize_paper",
                "description": "Summarize papers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "papers": {
                            "type": "string",
                            "description": "Papers to summarize"
                        }
                    },
                    "required": ["papers"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_research_report",
                "description": "Generate final report",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Report content"
                        }
                    },
                    "required": ["content"]
                }
            }
        }
    ]

    try:
        # Make an API call to Groq to generate the next thought and action
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="deepseek-r1-distill-llama-70b",
            max_tokens=100,
            tools=tools,
            tool_choice="auto"
        )

        # Extract the generated message
        message = response.choices[0].message
        content = message.content.strip() if message.content else ""

        # Parse the response to extract thought, action, and action_input
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            action = tool_call.function.name
            action_input = json.loads(tool_call.function.arguments)["query" if action == "search_academic_papers" else "papers" if action == "summarize_paper" else "content"]
            thought = content if content else f"Using {action} to progress research."
            return thought, action, action_input
        else:
            # Fallback: treat the entire content as a thought and continue with a search
            return content, "search_academic_papers", f"Find academic papers about {topic}"
            
    except Exception as e:
        print(f"Error in generate_thought_and_action: {str(e)}")
        # Fallback to basic search if there's an error
        return "Error occurred, falling back to basic search", "search_academic_papers", f"Find academic papers about {topic}"

def perform_action(action, action_input):
    """
    Execute research actions and return observations.
    
    :param action: The research action to perform
    :param action_input: The input for the action
    :return: The result of the action
    """
    if action == "search_academic_papers":
        # Use SerpAPI to search for academic papers
        params = {
            "engine": "google_scholar",
            "q": action_input,
            "api_key": os.environ.get("SERPER_API_KEY"),
            "num": 3,
            "as_ylo": "2020",  # Papers from 2020 onwards
            "hl": "en",  # English language
            "sort": "date"  # Sort by date
        }
        
        try:
            # Check if SERPER_API_KEY is set
            if not os.environ.get("SERPER_API_KEY"):
                return "Error: SERPER_API_KEY environment variable is not set"
                
            print(f"Searching for: {action_input}")  # Debug print
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "organic_results" in results and results["organic_results"]:
                papers = []
                for result in results["organic_results"]:
                    paper = {
                        "title": result.get("title", ""),
                        "authors": result.get("publication_info", {}).get("authors", ""),
                        "year": result.get("publication_info", {}).get("year", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "citations": result.get("inline_links", {}).get("cited_by", {}).get("total", 0)
                    }
                    papers.append(paper)
                
                if papers:
                    return json.dumps(papers, indent=2)
                else:
                    return f"No academic papers found for query: {action_input}"
            else:
                return f"No academic papers found for query: {action_input}"
                
        except Exception as e:
            return f"Error searching for academic papers: {str(e)}"
            
    elif action == "summarize_paper":
        try:
            papers = json.loads(action_input)
            summaries = []
            for paper in papers:
                summary = f"Title: {paper['title']}\nAuthors: {paper['authors']}\nYear: {paper['year']}\nCitations: {paper.get('citations', 'N/A')}\nSummary: {paper['snippet']}\n"
                summaries.append(summary)
            return "\n".join(summaries)
        except Exception as e:
            return f"Error summarizing papers: {str(e)}"
            
    elif action == "generate_research_report":
        try:
            # Create a structured research report
            report = f"""Research Report: {action_input}

Key Findings:
{action_input}

This report is based on the analysis of academic papers and their summaries."""
            return report
        except Exception as e:
            return f"Error generating research report: {str(e)}"
    else:
        return f"Invalid action: {action}"

# Demo
if __name__ == "__main__":
    
    
    topic = "Model Context Protocol"
    report = research_agent(topic)
    print(f"Final Report: {report}")
