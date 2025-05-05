import os
import json
from datetime import datetime
from typing import Dict, Any
from groq import Groq
from .models import Customer, CustomerStatus

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an admissions analyst for a 6-month applied AI bootcamp. Your task is to score customers based on their fit and intent.
Score each customer from 0-100 using the following rubric weights:
- Role seniority (15 points)
- Tech background (15 points)
- Goal alignment (15 points)
- Budget (10 points)
- Urgency (10 points)
- Webinar engagement (10 points)
- Question activity (7 points)
- Country/Timezone (6 points)
- Referral source (6 points)
- Past touchpoints (6 points)

Return a JSON object with 'score' (integer) and 'reasoning' (string, max 35 words).
Prioritize evaluating each dimension before issuing a conclusion."""

FEW_SHOT_EXAMPLES = [
    {
        "input": {
            "name": "Aditi",
            "title": "Senior ML Engineer",
            "goal": "Lead AI team",
            "budget": "company",
            "engaged_mins": 55,
            "country": "IN",
            "asked_question": True
        },
        "output": {
            "score": 88,
            "reasoning": "Senior engineer, strong goal alignment, budget secured, high engagement."
        }
    },
    {
        "input": {
            "name": "Raj",
            "title": "HR Associate",
            "goal": "Understand basics",
            "budget": "self",
            "engaged_mins": 5,
            "country": "IN",
            "asked_question": False
        },
        "output": {
            "score": 34,
            "reasoning": "Non-technical role, low engagement, unclear need, limited budget."
        }
    }
]

def build_prompt(customer_data: Dict[str, Any]) -> list:
    """Build the prompt for the Groq API."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add few-shot examples
    for example in FEW_SHOT_EXAMPLES:
        messages.append({
            "role": "user",
            "content": json.dumps(example["input"])
        })
        messages.append({
            "role": "assistant",
            "content": json.dumps(example["output"])
        })
    
    # Add the current customer data
    messages.append({
        "role": "user",
        "content": json.dumps(customer_data)
    })
    
    return messages

def calculate_engagement_score(engaged_mins: int) -> float:
    """Calculate engagement score based on webinar duration."""
    if engaged_mins <= 5:
        return 0.0
    elif engaged_mins <= 20:
        return 0.3
    elif engaged_mins <= 40:
        return 0.6
    else:
        return 1.0

async def qualify_customer(customer: Customer) -> Customer:
    """Qualify a customer using Groq LLM."""
    # Calculate engagement minutes if webinar data is available
    if customer.webinar_join and customer.webinar_leave:
        customer.engaged_mins = int((customer.webinar_leave - customer.webinar_join).total_seconds() / 60)
    
    # Prepare customer data for the prompt
    customer_data = {
        "name": customer.name,
        "title": customer.title,
        "goal": customer.goal,
        "budget": customer.budget,
        "engaged_mins": customer.engaged_mins or 0,
        "country": customer.country,
        "asked_question": customer.asked_question
    }
    
    # Get qualification from Groq
    messages = build_prompt(customer_data)
    response = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
        temperature=0.2
    )
    
    # Parse the response
    result = json.loads(response.choices[0].message.content)
    
    # Update customer with qualification results
    customer.score = result["score"]
    customer.reasoning = result["reasoning"]
    customer.status = CustomerStatus.SQL if customer.score >= 70 else CustomerStatus.NURTURE
    customer.updated_at = datetime.utcnow()
    
    return customer 