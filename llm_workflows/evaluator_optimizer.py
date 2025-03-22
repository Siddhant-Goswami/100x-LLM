import asyncio
from utils import get_llm_response

async def evaluator_optimizer_workflow(writing_prompt: str, max_iterations: int = 3):
    """Example of evaluator-optimizer pattern for iterative improvement"""
    
    print(f"Initial prompt: {writing_prompt}\n")
    
    # Initial draft by optimizer
    current_draft = get_llm_response(
        f"Write a response to: {writing_prompt}"
    )
    
    print("Initial draft:")
    print(current_draft)
    
    for i in range(max_iterations):
        print(f"\nIteration {i + 1}:")
        
        # Evaluator reviews the draft
        evaluation = get_llm_response(
            f"""Evaluate this text based on:
            1. Clarity
            2. Completeness
            3. Accuracy
            Provide specific improvement suggestions.
            
            Text: {current_draft}"""
        )
        
        print("\nEvaluation:")
        print(evaluation)
        
        # Check if quality is satisfactory
        quality_check = get_llm_response(
            f"Based on this evaluation, should the text be improved further? Answer only YES or NO: {evaluation}"
        )
        
        if quality_check.strip().upper() == "NO":
            print("\nQuality is satisfactory, stopping iterations.")
            break
        
        print("\nImproving based on feedback...")
        # Optimizer improves based on feedback
        current_draft = get_llm_response(
            f"""Improve this text based on the following feedback:
            Original: {current_draft}
            Feedback: {evaluation}"""
        )
        
        print("\nImproved draft:")
        print(current_draft)
    
    return current_draft, i + 1, evaluation

# Example usage
async def main():
    # Example writing prompt
    prompt = "What is ReAct Agent?"
    
    # Run the evaluator-optimizer workflow
    final_draft, iterations, final_evaluation = await evaluator_optimizer_workflow(prompt)
    
    print(f"\nFinal Results after {iterations} iterations:")
    print("\nFinal Draft:")
    print(final_draft)
    print("\nFinal Evaluation:")
    print(final_evaluation)

if __name__ == "__main__":
    asyncio.run(main()) 