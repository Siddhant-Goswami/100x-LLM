import os
import json
import time
from dotenv import load_dotenv
from groq import Groq
from typing import Dict, List, Optional, Tuple, Any
import logging
import pathlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("evaluator-optimizer")

# Load environment variables
load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=GROQ_API_KEY)

# Load configuration from environment variables
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "deepseek-r1-distill-llama-70b")
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "5"))
EARLY_TERMINATION_THRESHOLD = int(os.getenv("EARLY_TERMINATION_THRESHOLD", "90"))
COMPLETION_THRESHOLD = int(os.getenv("COMPLETION_THRESHOLD", "80"))
CATEGORY_THRESHOLD = int(os.getenv("CATEGORY_THRESHOLD", "16"))
MIN_IMPROVEMENT_THRESHOLD = int(os.getenv("MIN_IMPROVEMENT_THRESHOLD", "5"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./research_outputs")
SAVE_INTERIM_RESULTS = os.getenv("SAVE_INTERIM_RESULTS", "false").lower() == "true"

# Ensure output directory exists
pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# 100-point rubric for evaluating research content
EVALUATION_RUBRIC = {
    "Source Quality": {
        "description": "Quality, diversity, and reliability of information sources",
        "max_points": 20
    },
    "Analytical Depth": {
        "description": "Depth of analysis, critical thinking, and insight",
        "max_points": 20
    },
    "Technical Accuracy": {
        "description": "Accuracy of technical details and explanations",
        "max_points": 20
    },
    "Practical Applications": {
        "description": "Relevance and quality of real-world applications",
        "max_points": 20
    },
    "Communication Clarity": {
        "description": "Clarity, organization, and accessibility of content",
        "max_points": 20
    }
}

class AppliedAIResearchAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the Applied AI Research Agent.
        
        Args:
            model (str): The Groq model to use for generation
        """
        self.model = model
        self.client = client
        self.max_iterations = MAX_ITERATIONS
        self.early_termination_threshold = EARLY_TERMINATION_THRESHOLD
        self.completion_threshold = COMPLETION_THRESHOLD
        self.category_threshold = CATEGORY_THRESHOLD
        self.min_improvement_threshold = MIN_IMPROVEMENT_THRESHOLD
        
    def _generate_with_llm(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """
        Generate text using the Groq LLM.
        
        Args:
            prompt (str): The prompt to send to the LLM
            system_prompt (str, optional): The system prompt to use
            temperature (float, optional): Temperature for generation
            
        Returns:
            str: The generated text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in LLM generation: {str(e)}")
            raise
    
    def run_researcher(self, query: str, iteration: int = 1, 
                      previous_feedback: Optional[Dict] = None, 
                      focus_areas: Optional[List[str]] = None) -> str:
        """
        Run the Researcher (Optimizer) component to generate research content.
        
        Args:
            query (str): The research query
            iteration (int): Current iteration number
            previous_feedback (Dict, optional): Feedback from the previous evaluation
            focus_areas (List[str], optional): Areas to focus on for improvement
            
        Returns:
            str: The generated research content
        """
        system_prompt = """You are the Researcher component of an Applied AI Research Agent. 
Your task is to conduct comprehensive research on Applied AI topics and produce high-quality, 
structured content that meets academic and practical standards."""
        
        # Build the researcher prompt
        prompt = f"""You are the Researcher component of an Applied AI Research Agent. Your task is to {query}.

CURRENT ITERATION: {iteration}
"""
        
        if iteration > 1 and previous_feedback:
            prompt += f"""
PREVIOUS EVALUATION:
{previous_feedback}
"""
        
        if focus_areas:
            prompt += f"""
FOCUS AREAS FOR THIS ITERATION:
{', '.join(focus_areas)}
"""
        
        prompt += """
Conduct comprehensive research on this topic and produce a well-structured document that includes:
1. Executive summary with 3-5 key insights
2. Detailed analysis of all major subtopics
3. Technical explanations with clear definitions
4. Minimum 5 concrete examples and applications
5. Clear distinction between established knowledge, emerging trends, and speculative directions
6. At least 3 limitations and areas requiring further research
7. Minimum 5 specific implications for practitioners

Structure your output with logical hierarchy and numeric indices.
"""
        
        if iteration == 1:
            prompt += "\nSince this is iteration 1, focus on information gathering and comprehensive structure."
        elif iteration == 2:
            prompt += "\nSince this is iteration 2, focus on enhancing analytical depth and technical accuracy."
        else:
            prompt += "\nSince this is iteration 3+, focus on refining practical applications and clarity."
        
        logger.info(f"Running Researcher component (Iteration {iteration})")
        return self._generate_with_llm(prompt, system_prompt)
    
    def run_evaluator(self, research_content: str) -> Dict:
        """
        Run the Evaluator component to assess the quality of research content.
        
        Args:
            research_content (str): The research content to evaluate
            
        Returns:
            Dict: Evaluation results including scores and feedback
        """
        system_prompt = """You are the Evaluator component of an Applied AI Research Agent.
Your task is to objectively assess research content against a 100-point rubric and provide
specific, actionable feedback for improvement."""
        
        # Format the rubric for the prompt
        rubric_text = ""
        for category, details in EVALUATION_RUBRIC.items():
            rubric_text += f"{category} ({details['max_points']} points): {details['description']}\n"
        
        prompt = f"""You are the Evaluator component of an Applied AI Research Agent. Evaluate the research document against our 100-point rubric:

{rubric_text}

For each category:
1. Assign specific point values (out of 20)
2. Provide detailed feedback on strengths and weaknesses
3. Make specific, actionable recommendations for improvement

Calculate the total score and provide a comprehensive evaluation.

Identify the top 3 focus areas for the next iteration that would most improve the overall quality.

Here is the research content to evaluate:

{research_content}

Respond in JSON format with the following structure:
{{
  "category_scores": {{
    "Source Quality": <score>,
    "Analytical Depth": <score>,
    "Technical Accuracy": <score>,
    "Practical Applications": <score>,
    "Communication Clarity": <score>
  }},
  "category_feedback": {{
    "Source Quality": "<feedback>",
    "Analytical Depth": "<feedback>",
    "Technical Accuracy": "<feedback>",
    "Practical Applications": "<feedback>",
    "Communication Clarity": "<feedback>"
  }},
  "total_score": <total>,
  "focus_areas": ["<area1>", "<area2>", "<area3>"],
  "summary_feedback": "<overall feedback>"
}}
"""
        
        logger.info("Running Evaluator component")
        result = self._generate_with_llm(prompt, system_prompt)
        
        # Extract JSON from the result
        try:
            # Try to parse the entire response as JSON
            evaluation = json.loads(result)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the text
            try:
                json_str = result[result.find("{"):result.rfind("}")+1]
                evaluation = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse evaluator response as JSON: {str(e)}")
                # Fallback to a simple evaluation structure
                evaluation = {
                    "category_scores": {k: 0 for k in EVALUATION_RUBRIC.keys()},
                    "category_feedback": {k: "Error parsing feedback" for k in EVALUATION_RUBRIC.keys()},
                    "total_score": 0,
                    "focus_areas": ["Error parsing focus areas"],
                    "summary_feedback": "Error parsing evaluator response"
                }
        
        return evaluation
    
    def format_feedback_for_researcher(self, evaluation: Dict) -> str:
        """
        Format the evaluation feedback for the researcher.
        
        Args:
            evaluation (Dict): The evaluation results
            
        Returns:
            str: Formatted feedback
        """
        feedback = f"TOTAL SCORE: {evaluation['total_score']}/100\n\n"
        
        for category, score in evaluation['category_scores'].items():
            feedback += f"{category}: {score}/20\n"
            feedback += f"{evaluation['category_feedback'][category]}\n\n"
        
        feedback += "FOCUS AREAS FOR IMPROVEMENT:\n"
        for area in evaluation['focus_areas']:
            feedback += f"- {area}\n"
        
        feedback += f"\nSUMMARY: {evaluation['summary_feedback']}"
        
        return feedback
    
    def run_research_agent(self, query: str) -> Dict:
        """
        Run the complete Applied AI Research Agent workflow.
        
        Args:
            query (str): The research query
            
        Returns:
            Dict: Final results including research content and evaluation
        """
        iterations = 0
        max_iterations = self.max_iterations
        previous_score = 0
        evaluator_feedback = None
        research_content = None
        evaluation_history = []
        
        # For storing interim results if enabled
        interim_results = []
        
        while iterations < max_iterations:
            iterations += 1
            
            logger.info(f"Starting iteration {iterations}/{max_iterations}")
            
            # Determine focus areas
            focus_areas = None
            if iterations > 1 and 'focus_areas' in evaluation:
                focus_areas = evaluation['focus_areas']
            
            # Run researcher
            research_content = self.run_researcher(
                query=query,
                iteration=iterations,
                previous_feedback=evaluator_feedback,
                focus_areas=focus_areas
            )
            
            # Run evaluator
            evaluation = self.run_evaluator(research_content)
            current_score = evaluation['total_score']
            
            # Format feedback for the next iteration
            evaluator_feedback = self.format_feedback_for_researcher(evaluation)
            
            # Store evaluation history
            evaluation_history.append({
                'iteration': iterations,
                'score': current_score,
                'evaluation': evaluation
            })
            
            # Store interim results if enabled
            if SAVE_INTERIM_RESULTS:
                interim_results.append({
                    'iteration': iterations,
                    'content': research_content,
                    'evaluation': evaluation,
                    'feedback': evaluator_feedback
                })
                
                # Save interim result to file
                interim_filename = os.path.join(
                    OUTPUT_DIR, 
                    f"interim_result_iter{iterations}_{time.strftime('%Y%m%d-%H%M%S')}.json"
                )
                with open(interim_filename, 'w') as f:
                    json.dump(interim_results[-1], f, indent=2)
                logger.info(f"Saved interim result for iteration {iterations} to {interim_filename}")
            
            logger.info(f"Iteration {iterations} complete. Score: {current_score}/100")
            
            # Check termination conditions
            all_categories_meet_threshold = all(
                score >= self.category_threshold 
                for score in evaluation['category_scores'].values()
            )
            
            if (current_score >= self.early_termination_threshold and iterations >= 3) or \
               (current_score >= self.completion_threshold and all_categories_meet_threshold) or \
               (current_score - previous_score < self.min_improvement_threshold and iterations > 1) or \
               (iterations == max_iterations):
                logger.info(f"Termination condition met after {iterations} iterations")
                break
                
            previous_score = current_score
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        
        # Generate a final polished research report
        final_report = self.generate_final_report(query, research_content, evaluation, iterations)
        
        # Return final research content with evaluation metadata
        result = {
            'content': research_content,
            'final_evaluation': evaluation,
            'iterations': iterations,
            'evaluation_history': evaluation_history,
            'final_report': final_report
        }
        
        # Include interim results if enabled
        if SAVE_INTERIM_RESULTS:
            result['interim_results'] = interim_results
            
        return result
    
    def generate_final_report(self, query: str, research_content: str, evaluation: Dict, iterations: int) -> str:
        """
        Generate a final polished research report based on the research content and evaluation.
        
        Args:
            query (str): The original research query
            research_content (str): The final research content
            evaluation (Dict): The final evaluation results
            iterations (int): The number of iterations performed
            
        Returns:
            str: The formatted final research report
        """
        system_prompt = """You are a professional research report compiler.
Your task is to take research content and format it into a professional, well-structured
research report with proper formatting, sections, and metadata."""
        
        timestamp = time.strftime("%Y-%m-%d")
        
        # Build confidence ratings based on evaluation scores
        confidence_ratings = {}
        for category, score in evaluation['category_scores'].items():
            if score >= 18:
                confidence = "Very High"
            elif score >= 16:
                confidence = "High"
            elif score >= 14:
                confidence = "Moderate"
            elif score >= 12:
                confidence = "Low"
            else:
                confidence = "Very Low"
            confidence_ratings[category] = confidence
        
        prompt = f"""Format the following research content into a professional research report.

RESEARCH QUERY: {query}

METADATA:
- Date: {timestamp}
- Iterations: {iterations}
- Quality Score: {evaluation['total_score']}/100
- Confidence Ratings:
  - Source Quality: {confidence_ratings['Source Quality']}
  - Analytical Depth: {confidence_ratings['Analytical Depth']}
  - Technical Accuracy: {confidence_ratings['Technical Accuracy']}
  - Practical Applications: {confidence_ratings['Practical Applications']}
  - Communication Clarity: {confidence_ratings['Communication Clarity']}

REPORT CONTENT:
{research_content}

Please format this into a well-structured research report with:
1. A professional title page including the research query, date, and quality metrics
2. An executive summary
3. A table of contents
4. The main content properly structured with sections and subsections
5. Conclusion section
6. Appendix with confidence ratings and methodology notes (including that this was generated through {iterations} iterations of an AI research agent)

Ensure the formatting is professional and academic in style.
"""
        
        logger.info("Generating final research report")
        return self._generate_with_llm(prompt, system_prompt, temperature=0.3)

def save_final_report(report: str, query: str, output_dir: str = OUTPUT_DIR) -> str:
    """
    Save the final research report to a file.
    
    Args:
        report (str): The research report content
        query (str): The research query (used for filename)
        output_dir (str): Directory to save the report
        
    Returns:
        str: The path to the saved report file
    """
    # Generate a clean filename from the query
    clean_query = "".join(c if c.isalnum() else "_" for c in query[:30])
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"research_report_{clean_query}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Save the report to a markdown file
    with open(filepath, 'w') as f:
        f.write(report)
    
    return filepath

def main():
    """
    Main function to demonstrate the Applied AI Research Agent.
    """
    # Get the research query from command line arguments or use a default query
    import sys
    if len(sys.argv) > 1:
        research_query = " ".join(sys.argv[1:])
    else:
        research_query = "Investigate the current state and future potential of Large Language Models for code generation"
    
    # Create and run the agent
    agent = AppliedAIResearchAgent()
    
    logger.info(f"Starting Applied AI Research Agent with query: {research_query}")
    logger.info(f"Using model: {agent.model}")
    logger.info(f"Max iterations: {agent.max_iterations}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    result = agent.run_research_agent(research_query)
    
    # Generate a timestamped filename for raw data
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    json_filename = f"research_output_{timestamp}.json"
    json_filepath = os.path.join(OUTPUT_DIR, json_filename)
    
    # Save the full results to a JSON file
    with open(json_filepath, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Save the final report to a markdown file
    report_filepath = save_final_report(result['final_report'], research_query)
    
    logger.info(f"Research complete after {result['iterations']} iterations")
    logger.info(f"Final score: {result['final_evaluation']['total_score']}/100")
    logger.info(f"Raw data saved to {json_filepath}")
    logger.info(f"Final report saved to {report_filepath}")
    
    # Output a summary
    print("\n" + "="*50)
    print(f"Research Query: {research_query}")
    print(f"Iterations: {result['iterations']}")
    print(f"Final Score: {result['final_evaluation']['total_score']}/100")
    print("Category Scores:")
    for category, score in result['final_evaluation']['category_scores'].items():
        print(f"  - {category}: {score}/20")
    print("="*50)
    print(f"\nFinal Research Report saved to: {report_filepath}")
    print(f"Raw data (including all iterations) saved to: {json_filepath}")
    print("\nFirst 500 characters of the report:")
    print(result['final_report'][:500] + "...")

if __name__ == "__main__":
    main() 