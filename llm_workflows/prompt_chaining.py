from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define prompt templates
GENERATE_TEMPLATE = """Create compelling marketing copy for the following product:
Product: {product}
Target Audience: {target_audience}

The copy should be engaging, highlight key benefits, and resonate with the target audience.
Keep it concise but impactful."""

REVIEW_TEMPLATE = """Review and improve the following marketing copy:
Copy: {marketing_copy}

Check for:
1. Clarity and impact
2. Grammar and spelling
3. Brand voice consistency
4. Call to action effectiveness

Provide the improved version only."""

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

def generate_marketing_content(product: str, target_audience: str, target_language: str):
    """
    Generate, review, and translate marketing copy for a product.
    
    Args:
        product (str): The product to create marketing copy for
        target_audience (str): The target audience for the marketing copy
        target_language (str): The language to translate the copy into
        
    Returns:
        dict: Contains original copy, reviewed copy, and translated copy
    """
    # Generate initial copy
    generate_prompt = GENERATE_TEMPLATE.format(
        product=product,
        target_audience=target_audience
    )
    marketing_copy = get_completion(generate_prompt)
    
    # Review and improve the copy
    review_prompt = REVIEW_TEMPLATE.format(
        marketing_copy=marketing_copy
    )
    reviewed_copy = get_completion(review_prompt)
    
    # Translate the reviewed copy
    translate_prompt = TRANSLATE_TEMPLATE.format(
        reviewed_copy=reviewed_copy,
        target_language=target_language
    )
    translated_copy = get_completion(translate_prompt)
    
    return {
        "marketing_copy": marketing_copy,
        "reviewed_copy": reviewed_copy,
        "translated_copy": translated_copy
    }

# Example usage
if __name__ == "__main__":
    result = generate_marketing_content(
        product="Smart Fitness Watch",
        target_audience="Health-conscious young professionals",
        target_language="Spanish"
    )
    
    print("\nOriginal Copy:")
    print(result["marketing_copy"])
    print("\nReviewed Copy:")
    print(result["reviewed_copy"])
    print("\nTranslated Copy (Spanish):")
    print(result["translated_copy"]) 