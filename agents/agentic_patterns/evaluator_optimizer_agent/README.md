# Applied AI Research Agent: Evaluator-Optimizer Workflow

This package implements an Applied AI Research Agent using an Evaluator-Optimizer workflow, powered by Groq's Large Language Models. The agent iteratively generates and refines research content on Applied AI topics by conducting multiple rounds of evaluation and improvement.

## Architecture

The system consists of two primary components:
1. **Researcher (Optimizer)**: Generates research content on Applied AI topics
2. **Evaluator**: Assesses content quality against a 100-point rubric and provides specific feedback

These components operate in an iterative loop until quality thresholds are met, orchestrated by a Controller.

## Workflow Sequence

1. Initial Query Processing
   - Breaks research query into key components and subtopics
   - Identifies specific research questions
   - Defines scope boundaries

2. First Research Iteration
   - Researcher generates initial content focusing on information gathering and structure
   - Content covers all required sections from the rubric

3. First Evaluation
   - Evaluator scores the content against the 100-point rubric
   - Provides specific scores for each category
   - Generates detailed feedback identifying strengths and weaknesses
   - Prioritizes improvements for next iteration

4. Subsequent Iterations (2-5 total)
   - Researcher receives evaluator feedback
   - Improves content based on specific recommendations
   - Focuses on categories scoring below threshold (16/20)
   - Each iteration aims to improve total score by at least 5 points

5. Termination Conditions
   - Early termination: ≥90/100 points after 3 iterations
   - Standard completion: ≥80/100 points with ≥16/20 in each category
   - Maximum 5 iterations (to prevent diminishing returns)
   - Failure to improve by 5+ points in an iteration

6. Final Output Delivery
   - Final research report with all required sections
   - Self-evaluation scores included as metadata
   - Confidence ratings for major conclusions

## Installation

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `example.env` to `.env` and add your Groq API key:
   ```
   cp example.env .env
   # Edit .env with your API key
   ```

## Usage

### Command Line

Run the agent with a research query:

```bash
python evaluator_optimizer.py "Research query here"
```

If no query is provided, a default query about LLMs for code generation will be used.

### Python API

```python
from evaluator_optimizer import AppliedAIResearchAgent

# Create the agent
agent = AppliedAIResearchAgent()

# Run the agent with a research query
result = agent.run_research_agent("Research query here")

# Access the results
content = result['content']  # The original research content
final_report = result['final_report']  # The formatted research report
evaluation = result['final_evaluation']  # Final evaluation data
total_score = evaluation['total_score']  # Final score out of 100

# Save the final report to a file
from evaluator_optimizer import save_final_report
report_filename = save_final_report(result['final_report'], "Research query here")
```

## Evaluation Rubric

The agent evaluates research content against a 100-point rubric with five categories:

1. **Source Quality** (20 points): Quality, diversity, and reliability of information sources
2. **Analytical Depth** (20 points): Depth of analysis, critical thinking, and insight
3. **Technical Accuracy** (20 points): Accuracy of technical details and explanations
4. **Practical Applications** (20 points): Relevance and quality of real-world applications
5. **Communication Clarity** (20 points): Clarity, organization, and accessibility of content

## Output

The agent generates two main output files:

### 1. Research Report (Markdown)

A professionally formatted research report including:
- Title page with research query, date, and quality metrics
- Executive summary with key insights
- Table of contents
- Well-structured main content with sections and subsections
- Conclusion
- Appendix with confidence ratings and methodology notes

The report is saved as a markdown file with a filename based on the research query.

### 2. Raw Data (JSON)

Complete data from the research process including:
- `content`: The original unformatted research content
- `final_report`: The formatted research report
- `final_evaluation`: Detailed evaluation data
- `iterations`: Number of iterations performed
- `evaluation_history`: Score and feedback history across iterations

The raw data is saved as a JSON file with a timestamp in the name.

## Requirements

- Python 3.7+
- Groq API key
- Required packages (see requirements.txt)

## Models

By default, the agent uses the DeepSeek R1 model from Groq. You can specify a different model by editing the `.env` file or modifying the code directly.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 