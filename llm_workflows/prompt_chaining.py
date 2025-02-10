from groq import Groq
import os
from dotenv import load_dotenv
from typing import Dict, Tuple, Optional

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define prompt templates
GENERATE_TEMPLATE = """Create compelling marketing copy for the following product:
Product: {product}
Target Audience: {target_audience}
Requirements: {requirements}

{feedback_note}

The copy should be engaging, highlight key benefits, and resonate with the target audience.
Keep it concise but impactful."""

REVIEW_TEMPLATE = """Review the following marketing copy and determine if it meets the requirements:
Copy: {marketing_copy}
Product: {product}
Target Audience: {target_audience}
Requirements: {requirements}

Check for:
1. Clarity and impact
2. Grammar and spelling
3. Brand voice consistency
4. Call to action effectiveness
5. Alignment with requirements

Provide your response in the following format:
APPROVED: [true/false]
FEEDBACK: [detailed feedback if not approved, or improvement suggestions if approved]
IMPROVED_COPY: [improved version of the copy if approved, otherwise leave empty]"""

TRANSLATE_TEMPLATE = """Translate the following marketing copy to {target_language}:
Copy: {reviewed_copy}

Ensure the translation:
1. Maintains the original message and tone
2. Is culturally appropriate
3. Uses natural language in the target language
4. Preserves marketing impact

Provide the translation only."""

def get_completion(prompt: str) -> str:
    """
    Get completion from Groq API
    """
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def parse_review_response(response: str) -> Tuple[bool, str, Optional[str]]:
    """
    Parse the review response to extract approval status, feedback, and improved copy.
    
    Returns:
        Tuple[bool, str, Optional[str]]: (is_approved, feedback, improved_copy)
    """
    lines = response.split('\n')
    is_approved = False
    feedback = ""
    improved_copy = None
    
    for line in lines:
        if line.startswith("APPROVED:"):
            is_approved = "true" in line.lower()
        elif line.startswith("FEEDBACK:"):
            feedback = line.replace("FEEDBACK:", "").strip()
        elif line.startswith("IMPROVED_COPY:"):
            improved_copy = line.replace("IMPROVED_COPY:", "").strip()
            
    return is_approved, feedback, improved_copy

def generate_marketing_content(
    product: str,
    target_audience: str,
    requirements: str,
    target_language: str,
    max_attempts: int = 3
) -> Dict[str, str]:
    """
    Generate, review, and translate marketing copy for a product with feedback loop.
    
    Args:
        product (str): The product to create marketing copy for
        target_audience (str): The target audience for the marketing copy
        requirements (str): Specific requirements for the marketing copy
        target_language (str): The language to translate the copy into
        max_attempts (int): Maximum number of attempts to generate acceptable copy
        
    Returns:
        dict: Contains original copy, review status, feedback, and translated copy
    """
    attempt = 0
    feedback = ""
    
    while attempt < max_attempts:
        # Generate initial copy
        feedback_note = f"\nPrevious feedback to address: {feedback}" if feedback else ""
        generate_prompt = GENERATE_TEMPLATE.format(
            product=product,
            target_audience=target_audience,
            requirements=requirements,
            feedback_note=feedback_note
        )
        marketing_copy = get_completion(generate_prompt)
        
        # Review the copy
        review_prompt = REVIEW_TEMPLATE.format(
            marketing_copy=marketing_copy,
            product=product,
            target_audience=target_audience,
            requirements=requirements
        )
        review_response = get_completion(review_prompt)
        is_approved, feedback, improved_copy = parse_review_response(review_response)
        
        if is_approved:
            # Use the improved copy if available, otherwise use the original
            final_copy = improved_copy if improved_copy else marketing_copy
            
            # Translate the approved copy
            translate_prompt = TRANSLATE_TEMPLATE.format(
                reviewed_copy=final_copy,
                target_language=target_language
            )
            translated_copy = get_completion(translate_prompt)
            
            return {
                "status": "success",
                "original_copy": marketing_copy,
                "final_copy": final_copy,
                "translated_copy": translated_copy,
                "feedback": feedback,
                "attempts": attempt + 1
            }
        
        attempt += 1
        if attempt == max_attempts:
            return {
                "status": "failed",
                "original_copy": marketing_copy,
                "feedback": feedback,
                "attempts": attempt
            }
    
# Example usage
if __name__ == "__main__":
    result = generate_marketing_content(
        product="Smart Fitness Watch",
        target_audience="Health-conscious young professionals",
        requirements="""
        - Emphasize AI-powered health tracking features
        - Include mention of battery life
        - Focus on work-life balance benefits
        - Keep it under 100 words
        """,
        target_language="Spanish"
    )
    
    print("\nStatus:", result["status"])
    print("\nOriginal Copy:")
    print(result["original_copy"])
    
    if result["status"] == "success":
        print("\nFinal Copy:")
        print(result["final_copy"])
        print("\nTranslated Copy (Spanish):")
        print(result["translated_copy"])
    
    print("\nFeedback:")
    print(result["feedback"])
    print("\nNumber of attempts:", result["attempts"]) 