import os
import json
import logging
import time
from datetime import datetime
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
evaluation_history = []

# Evaluation rubric
EVALUATION_RUBRIC = {
    "Tool Usage Effectiveness": {
        "max_points": 20,
        "description": "Web search query precision, data analytics approach selection, tool combination strategy, tool output interpretation"
    },
    "Source Quality": {
        "max_points": 20,
        "description": "High-quality sources from search results, recency of retrieved information, diversity of sources, expert sources identified"
    },
    "Data-Driven Insights": {
        "max_points": 20,
        "description": "Quantitative findings extracted, statistical significance evaluated, data visualization relevance, pattern identification"
    },
    "Research Depth": {
        "max_points": 20,
        "description": "Technical concept exploration, multiple perspective integration, state-of-the-art coverage, future directions identified"
    },
    "Actionable Output": {
        "max_points": 20,
        "description": "Practical recommendations, implementation guidance, limitation awareness, decision-making support"
    }
}

def add_to_memory(entry_type, content, confidence=None):
    """Add an entry to the agent's memory with optional confidence level"""
    entry = {
        "type": entry_type,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    if confidence is not None:
        entry["confidence"] = confidence
    memory.append(entry)
    logger.info(f"Added to memory: {entry_type} - {content[:100]}...")

def get_memory_as_text():
    """Convert memory to text format for LLM context"""
    memory_text = ""
    for entry in memory:
        prefix = "Thought: " if entry["type"] == "thought" else "Observation: "
        memory_text += f"{prefix}{entry['content']}\n"
        if "confidence" in entry:
            memory_text += f"Confidence: {entry['confidence']}/10\n"
        memory_text += "\n"
    return memory_text

def evaluate_research(report, memory_entries):
    """Evaluate research quality using the 100-point rubric"""
    logger.info("Evaluating research quality...")
    
    # Format the rubric for the prompt
    rubric_text = ""
    for category, details in EVALUATION_RUBRIC.items():
        rubric_text += f"{category} ({details['max_points']} points): {details['description']}\n"
    
    prompt = f"""Evaluate the research document against our 100-point rubric:

{rubric_text}

For each category:
1. Assign specific point values (out of 20)
2. Provide detailed feedback on strengths and weaknesses
3. Make specific, actionable recommendations for improvement

Calculate the total score and provide a comprehensive evaluation.

Identify the top 3 focus areas for the next iteration that would most improve the overall quality.

Here is the research content to evaluate:

{report}

Respond in JSON format with the following structure:
{{
  "category_scores": {{
    "Tool Usage Effectiveness": <score>,
    "Source Quality": <score>,
    "Data-Driven Insights": <score>,
    "Research Depth": <score>,
    "Actionable Output": <score>
  }},
  "category_feedback": {{
    "Tool Usage Effectiveness": "<feedback>",
    "Source Quality": "<feedback>",
    "Data-Driven Insights": "<feedback>",
    "Research Depth": "<feedback>",
    "Actionable Output": "<feedback>"
  }},
  "total_score": <total>,
  "focus_areas": ["<area1>", "<area2>", "<area3>"],
  "summary_feedback": "<overall feedback>"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000,
        response_format={"type": "json_object"}
    )
    
    evaluation = json.loads(response.choices[0].message.content.strip())
    evaluation_history.append({
        "iteration": len(evaluation_history) + 1,
        "timestamp": datetime.now().isoformat(),
        "evaluation": evaluation
    })
    
    logger.info(f"Evaluation complete. Total score: {evaluation['total_score']}/100")
    return evaluation

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
        temperature=0.2,
        max_tokens=300
    )
    thought = response.choices[0].message.content.strip()
    add_to_memory("thought", thought)
    return thought

def web_search(query, result_count=5, date_filter="all"):
    """Perform a web search using SerpAPI with enhanced filtering and analytics"""
    logger.info(f"Performing web search for: {query}")
    params = {
        "q": query,
        "api_key": serpapi_key,
        "num": result_count
    }
    
    # Add date filtering if specified
    if date_filter == "recent":
        params["time"] = "year"
    elif date_filter == "latest":
        params["time"] = "month"
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if "organic_results" in results:
        top_results = results["organic_results"][:result_count]
        
        # Analyze source quality and extract insights
        source_analysis = analyze_sources(top_results)
        insights = extract_insights(top_results, source_analysis)
        
        result_text = "\n\n".join([
            f"Title: {r['title']}\n"
            f"Snippet: {r['snippet']}\n"
            f"Source: {r.get('link', 'N/A')}\n"
            f"Date: {r.get('date', 'N/A')}\n"
            f"Quality Score: {source_analysis.get(r.get('link', ''), {}).get('quality_score', 'N/A')}"
            for r in top_results
        ])
        
        add_to_memory("observation", f"Search results for '{query}':\n{result_text}")
        add_to_memory("analysis", f"Source quality analysis:\n{json.dumps(source_analysis, indent=2)}")
        add_to_memory("insights", f"Key insights extracted:\n{json.dumps(insights, indent=2)}")
        
        logger.info(f"Found {len(top_results)} results for query: {query}")
        return result_text, source_analysis, insights
    else:
        add_to_memory("observation", f"No results found for '{query}'.")
        logger.warning(f"No results found for query: {query}")
        return "No results found.", {}, {}

def analyze_sources(results):
    """Analyze the quality and reliability of search results"""
    source_analysis = {}
    
    for result in results:
        url = result.get('link', '')
        if not url:
            continue
            
        # Basic quality indicators
        quality_score = 0
        indicators = {
            "is_academic": any(domain in url.lower() for domain in ['.edu', '.ac.', 'arxiv.org', 'researchgate.net']),
            "is_authoritative": any(domain in url.lower() for domain in ['.gov', '.org', 'wikipedia.org']),
            "has_date": bool(result.get('date')),
            "has_author": bool(result.get('author')),
            "has_citations": bool(result.get('citations'))
        }
        
        # Calculate quality score based on indicators
        quality_score = sum(2 for value in indicators.values() if value)
        
        source_analysis[url] = {
            "quality_score": quality_score,
            "indicators": indicators,
            "domain": url.split('/')[2] if len(url.split('/')) > 2 else url
        }
    
    return source_analysis

def extract_insights(results, source_analysis):
    """Extract key insights and patterns from search results"""
    insights = {
        "key_findings": [],
        "patterns": [],
        "statistics": {},
        "confidence_levels": {}
    }
    
    # Extract key findings and patterns
    for result in results:
        snippet = result.get('snippet', '')
        if not snippet:
            continue
            
        # Look for numerical data and statistics
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?%?', snippet)
        if numbers:
            insights["statistics"][result.get('title', '')] = numbers
            
        # Look for key findings (statements with high confidence)
        if any(phrase in snippet.lower() for phrase in ['proves', 'demonstrates', 'shows', 'confirms']):
            insights["key_findings"].append(snippet)
            
        # Look for patterns (recurring themes)
        if any(phrase in snippet.lower() for phrase in ['trend', 'pattern', 'tendency', 'typically']):
            insights["patterns"].append(snippet)
            
        # Assign confidence levels based on source quality
        url = result.get('link', '')
        if url in source_analysis:
            insights["confidence_levels"][result.get('title', '')] = source_analysis[url]["quality_score"] / 2
    
    return insights

def search_academic_papers(query):
    """Search for academic papers related to the query with enhanced filtering"""
    logger.info(f"Searching for academic papers on: {query}")
    
    # Construct academic-specific query
    academic_query = f"{query} research paper academic"
    results, source_analysis, insights = web_search(academic_query, result_count=5, date_filter="recent")
    
    # Extract potential paper information with quality assessment
    paper_count_before = len(papers)
    for line in results.split('\n'):
        if line.startswith("Title:") and ("paper" in line.lower() or "research" in line.lower()):
            paper_title = line.replace("Title:", "").strip()
            source_url = line.split("Source: ")[1].split("\n")[0] if "Source: " in line else None
            
            paper = {
                "title": paper_title,
                "read": False,
                "source_url": source_url,
                "quality_score": source_analysis.get(source_url, {}).get("quality_score", 0) if source_url else 0
            }
            papers.append(paper)
    
    paper_list = "\n".join([
        f"- {p['title']} (Quality Score: {p['quality_score']})"
        for p in papers
    ])
    add_to_memory("observation", f"Potential papers identified:\n{paper_list}")
    
    papers_found = len(papers) - paper_count_before
    logger.info(f"Identified {papers_found} new potential papers")
    return results, source_analysis, insights

def summarize_paper(paper_idx):
    """Summarize a paper using the LLM with enhanced analysis"""
    logger.info(f"Attempting to summarize paper at index: {paper_idx}")
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
        search_results, source_analysis, insights = web_search(
            f"{paper['title']} abstract methodology results",
            result_count=3,
            date_filter="recent"
        )
        paper['content'] = search_results
        paper['source_analysis'] = source_analysis
        paper['insights'] = insights
        paper['read'] = True
        add_to_memory("observation", f"Retrieved content for paper: {paper['title']}")
    
    prompt = f"""
    Analyze and summarize the following research paper content in a structured way:

    PAPER TITLE: {paper['title']}
    PAPER CONTENT: {paper.get('content', 'No content available')}
    SOURCE ANALYSIS: {json.dumps(paper.get('source_analysis', {}), indent=2)}
    KEY INSIGHTS: {json.dumps(paper.get('insights', {}), indent=2)}

    Provide a comprehensive analysis covering:
    1. Main objectives and research questions
    2. Methodology and approach
    3. Key findings and results
    4. Statistical significance and data analysis
    5. Limitations and future work
    6. Practical implications
    7. Quality assessment and confidence level

    For each section, include:
    - Clear explanations of technical concepts
    - Quantitative data where available
    - Confidence levels for key claims
    - Connections to other research
    - Practical applications

    Format the summary with clear section headings and bullet points where appropriate.
    """

    logger.info("Generating paper summary...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    
    summary = response.choices[0].message.content.strip()
    paper['summary'] = summary
    
    # Calculate overall confidence level based on source quality and content analysis
    confidence = calculate_paper_confidence(paper)
    paper['confidence'] = confidence
    
    add_to_memory("observation", f"Generated summary for paper: {paper['title']} (Confidence: {confidence}/10)")
    logger.info(f"Successfully summarized paper: {paper['title']}")
    return summary

def calculate_paper_confidence(paper):
    """Calculate overall confidence level for a paper"""
    confidence = 0
    
    # Base confidence from source quality
    if 'source_analysis' in paper:
        source_url = paper.get('source_url')
        if source_url and source_url in paper['source_analysis']:
            confidence += paper['source_analysis'][source_url]['quality_score']
    
    # Additional confidence from content analysis
    if 'insights' in paper:
        insights = paper['insights']
        # Add confidence for having key findings
        confidence += len(insights.get('key_findings', [])) * 2
        # Add confidence for having statistics
        confidence += len(insights.get('statistics', {})) * 2
        # Add confidence for having patterns
        confidence += len(insights.get('patterns', []))
    
    # Normalize confidence to 1-10 scale
    confidence = min(10, max(1, confidence / 2))
    return confidence

def generate_research_report(topic):
    """Generate a research report on the topic with enhanced analysis"""
    logger.info(f"Generating research report on: {topic}")
    
    # Collect all paper summaries and metadata
    summaries = []
    for paper in papers:
        if 'summary' in paper:
            summaries.append({
                "title": paper['title'],
                "summary": paper['summary'],
                "confidence": paper.get('confidence', 5),
                "source_analysis": paper.get('source_analysis', {}),
                "insights": paper.get('insights', {})
            })
    
    # Calculate overall research confidence
    overall_confidence = sum(p.get('confidence', 5) for p in papers) / len(papers) if papers else 5
    
    # Format summaries for the prompt
    summaries_text = "\n\n".join([
        f"## {s['title']}\n\n{s['summary']}\n\n"
        f"Confidence Level: {s['confidence']}/10\n"
        f"Key Insights: {json.dumps(s['insights'], indent=2)}"
        for s in summaries
    ])
    
    logger.info(f"Including {len(summaries)} paper summaries in the report")
    
    prompt = f"""
    Create a comprehensive research report on the topic "{topic}" based on the following paper summaries:

    {summaries_text}

    Your report should include:
    1. Executive Summary
       - Key findings and insights
       - Overall confidence level ({overall_confidence:.1f}/10)
       - Research methodology overview
    
    2. Detailed Analysis
       - Technical concepts and definitions
       - Quantitative findings and statistics
       - Pattern analysis and trends
       - Comparative assessment
    
    3. Source Quality Assessment
       - Source diversity and recency
       - Authority and reliability
       - Methodological rigor
    
    4. Practical Applications
       - Implementation considerations
       - Resource requirements
       - Success metrics
       - Case studies
    
    5. Limitations and Future Work
       - Current challenges
       - Research gaps
       - Future directions
    
    6. Conclusion
       - Key takeaways
       - Recommendations
       - Action items

    FORMAT THE REPORT WITH MARKDOWN HEADINGS AND INCLUDE:
    - Clear section hierarchy
    - Bullet points for key points
    - Tables for comparative data
    - Confidence levels for major claims
    - Implementation difficulty ratings (1-10)
    """

    logger.info("Generating final research report...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    report = response.choices[0].message.content.strip()
    add_to_memory("observation", "Generated final research report")
    
    # Evaluate the report
    evaluation = evaluate_research(report, memory)
    
    # Add evaluation metadata to the report
    report = f"""
# Research Report: {topic}

## Metadata
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Overall Confidence: {overall_confidence:.1f}/10
- Quality Score: {evaluation['total_score']}/100
- Iterations: {len(evaluation_history)}

## Evaluation Summary
{json.dumps(evaluation['category_scores'], indent=2)}

{report}
"""
    
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

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        
        if not response or not response.choices:
            logger.warning("No response received from OpenAI API")
            return "search_academic_papers", {"query": "AI Agents research"}
            
        content = response.choices[0].message.content
        if not content:
            logger.warning("Empty response content from OpenAI API")
            return "search_academic_papers", {"query": "AI Agents research"}
            
        action_json = content.strip()
        try:
            action_data = json.loads(action_json)
            action = action_data["action"]
            params = action_data.get("params", {})
            
            # Validate action
            valid_actions = ["search_academic_papers", "summarize_paper", "generate_research_report"]
            if action not in valid_actions:
                logger.warning(f"Invalid action received: {action}")
                return "search_academic_papers", {"query": "AI Agents research"}
            
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
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse action JSON: {str(e)}")
            return "search_academic_papers", {"query": "AI Agents research"}
            
    except Exception as e:
        error_msg = f"Error in decide_next_action: {str(e)}"
        add_to_memory("observation", error_msg)
        logger.error(error_msg)
        return "search_academic_papers", {"query": "AI Agents research"}

def research(topic, max_steps=3, min_score=80, min_improvement=5):
    """Main research function implementing the enhanced ReAct loop with evaluation"""
    logger.info(f"Starting research on topic: {topic} with max_steps: {max_steps}")
    
    # Clear global state for new research
    global memory, papers, evaluation_history
    memory = []
    papers = []
    evaluation_history = []
    
    # Initialize research state
    current_score = 0
    previous_score = 0
    iterations = 0
    
    add_to_memory("thought", f"Starting research on topic: {topic}")
    
    while iterations < max_steps:
        iterations += 1
        logger.info(f"Research step {iterations}/{max_steps}")
        
        # First, reason about the current state
        reason(get_memory_as_text())
        
        # Then, decide and execute the next action
        action, params = decide_next_action()
        
        if action == "search_academic_papers":
            results, source_analysis, insights = search_academic_papers(params.get("query", topic))
        elif action == "summarize_paper":
            paper_idx = params.get("paper_idx", 0)
            if isinstance(paper_idx, str):
                try:
                    paper_idx = int(paper_idx)
                except ValueError:
                    logger.warning(f"Converting invalid paper_idx string '{paper_idx}' to 0")
                    paper_idx = 0
            summarize_paper(paper_idx)
        elif action == "generate_research_report":
            logger.info("Generating final report and ending research process")
            report = generate_research_report(params.get("topic", topic))
            
            # Evaluate the report
            evaluation = evaluate_research(report, memory)
            current_score = evaluation['total_score']
            
            # Check if we've met our quality criteria
            all_categories_meet_threshold = all(
                score >= 16  # 80% threshold per category
                for score in evaluation['category_scores'].values()
            )
            
            if current_score >= min_score and all_categories_meet_threshold:
                logger.info(f"Research quality criteria met (Score: {current_score}/100)")
                return report
            
            # Check if we've made sufficient improvement
            if iterations > 1 and current_score - previous_score < min_improvement:
                logger.info(f"Insufficient improvement in score ({current_score - previous_score} points)")
                return report
            
            # If we haven't met criteria, continue with next iteration
            previous_score = current_score
            continue
    
    # If we've reached max steps, generate a final report
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
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
report_filename = f"react_research_report_{timestamp}.md"
with open(report_filename, "w") as f:
    f.write(report)
        
print(f"\nReport saved to {report_filename}")
logger.info(f"Research report saved to {report_filename}")
        
# Save evaluation history
eval_filename = f"react_evaluation_history_{timestamp}.json"
with open(eval_filename, "w") as f:
    json.dump(evaluation_history, f, indent=2)
        
print(f"Evaluation history saved to {eval_filename}")
logger.info(f"Evaluation history saved to {eval_filename}")