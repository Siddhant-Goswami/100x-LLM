from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from datetime import datetime
import requests
import json
import os
from enum import Enum
import csv
import pathlib
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# Define the CSV file path
CSV_FILE = "ai_crm/customers.csv"

class Status(str, Enum):
    QUALIFIED = "Qualified"
    NURTURE = "Nurture"

class BudgetType(str, Enum):
    SELF = "Self"
    COMPANY = "Company"

# 1. Define the blueprint for APIs
class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    country: Optional[str] = None
    goal: Optional[str] = None
    budget: Optional[BudgetType] = None
    webinar_join: Optional[datetime] = None
    webinar_leave: Optional[datetime] = None
    asked_q: Optional[bool] = False
    referred: Optional[bool] = False
    past_touchpoints: Optional[int] = 0
    engaged_mins: Optional[float] = None
    score: Optional[float] = None
    reasoning: Optional[str] = None
    status: Optional[Status] = None

# CSV Database functions
def ensure_csv_exists():
    """Create the CSV file if it doesn't exist"""
    csv_path = pathlib.Path(CSV_FILE)
    if not csv_path.parent.exists():
        csv_path.parent.mkdir(parents=True)
    
    if not csv_path.exists():
        fieldnames = [field for field in Customer.__annotations__]
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

def read_customers_from_csv() -> List[Customer]:
    """Read customers from CSV file"""
    ensure_csv_exists()
    customers = []
    
    with open(CSV_FILE, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Handle empty strings and convert to appropriate types
            
            # Set empty strings to None for various fields
            for field in row:
                if row[field] == '':
                    row[field] = None
            
            # Convert numeric and boolean fields
            if row['id'] is not None:
                row['id'] = int(row['id'])
            
            if row['asked_q'] is not None:
                row['asked_q'] = row['asked_q'].lower() == 'true'
            
            if row['referred'] is not None:
                row['referred'] = row['referred'].lower() == 'true'
            
            if row['past_touchpoints'] is not None:
                row['past_touchpoints'] = int(row['past_touchpoints'])
            
            if row['engaged_mins'] is not None:
                row['engaged_mins'] = float(row['engaged_mins'])
            
            if row['score'] is not None:
                row['score'] = float(row['score'])
                
            if row['webinar_join'] is not None:
                row['webinar_join'] = datetime.fromisoformat(row['webinar_join'])
                
            if row['webinar_leave'] is not None:
                row['webinar_leave'] = datetime.fromisoformat(row['webinar_leave'])
                
            customers.append(Customer(**row))
    
    return customers

def write_customers_to_csv(customers: List[Customer]):
    """Write customers to CSV file"""
    ensure_csv_exists()
    
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = [field for field in Customer.__annotations__]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for customer in customers:
            # Convert customer model to dict and ensure all values are string-serializable
            customer_dict = jsonable_encoder(customer)
            writer.writerow(customer_dict)

# 2. Create the API endpoint

#Create
@app.post("/customers", response_model=Customer)
def create_customer(customer: Customer):
    # Calculate engaged minutes if not already calculated
    if not customer.engaged_mins and customer.webinar_join and customer.webinar_leave:
        customer.engaged_mins = calculate_engaged_minutes(customer)
    
    # Read existing customers
    customers_list = read_customers_from_csv()
    
    # Check if ID already exists
    for existing_customer in customers_list:
        if existing_customer.id == customer.id:
            raise HTTPException(status_code=400, detail="Customer with this ID already exists")
    
    # Add customer to the list
    customers_list.append(customer)
    
    # Write back to CSV
    write_customers_to_csv(customers_list)
    
    # Then qualify the customer
    return qualify_customer(customer.id)

#Read
@app.get("/customers", response_model=List[Customer])
def get_customers():
    return read_customers_from_csv()

#Update
@app.put("/customers/{id}", response_model=Customer)
def update_customer(id: int, customer: Customer):
    customers_list = read_customers_from_csv()
    
    for i, existing_customer in enumerate(customers_list):
        if existing_customer.id == id:
            customers_list[i] = customer
            write_customers_to_csv(customers_list)
            return customer
    
    raise HTTPException(status_code=404, detail="Customer not found")

#Delete
@app.delete("/customers/{id}", response_model=Customer)
def delete_customer(id: int):
    customers_list = read_customers_from_csv()
    
    for i, customer in enumerate(customers_list):
        if customer.id == id:
            deleted_customer = customers_list.pop(i)
            write_customers_to_csv(customers_list)
            return deleted_customer
    
    raise HTTPException(status_code=404, detail="Customer not found")

# 3. Lead Qualification Engine

def calculate_engaged_minutes(customer: Customer) -> float:
    """Calculate the engaged minutes based on webinar join and leave times"""
    if customer.webinar_join and customer.webinar_leave:
        engaged_time = (customer.webinar_leave - customer.webinar_join).total_seconds() / 60
        return round(engaged_time, 2)
    return 0.0

def qualify_lead_with_llm(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Use Groq LLM to qualify the lead and provide reasoning"""
    # Example leads for few-shot learning
    example_qualified = {
        "id": 12345,
        "name": "John Doe",
        "email": "johndoe@example.com",
        "phone": "+1234567890",
        "country": "India",
        "goal": "Become an AI PM",
        "budget": "Self",
        "webinar_join": "2025-05-08 10:00",
        "webinar_leave": "2025-05-08 11:00",
        "asked_q": True,
        "referred": False,
        "past_touchpoints": 5,
        "engaged_mins": 60,
        "score": 85,
        "reasoning": "John attended the entire webinar (60 mins), asked questions, and his goal aligns perfectly with the program. He is self-funded, making him a high-priority lead.",
        "status": "Qualified"
    }
    
    example_nurture = {
        "id": 67890,
        "name": "Jane Smith",
        "email": "janesmith@example.com",
        "phone": "+9876543210",
        "country": "USA",
        "goal": "Learn basic AI skills",
        "budget": "Company",
        "webinar_join": "2025-05-08 10:30",
        "webinar_leave": "2025-05-08 10:45",
        "asked_q": False,
        "referred": True,
        "past_touchpoints": 2,
        "engaged_mins": 15,
        "score": 55,
        "reasoning": "Jane was only engaged for 15 minutes, didn't ask any questions, and her goal doesn't align well with the cohort's focus on AI PM roles. She is referred, but her engagement is low.",
        "status": "Nurture"
    }
    
    # Prepare prompt for LLM with few-shot examples
    prompt = f"""
    You are a lead qualification expert for 100xEngineers. Your task is to score a potential customer based on the following rubrics:
    
    1. Fit (40%): Alignment with 100xEngineers' target audience (professionals in AI, tech, design, etc.). Higher weight for leads with clear goals aligned with the program.
    2. Engagement (25%): Interaction during the webinar (minutes attended, questions asked). More engagement equals higher score.
    3. Intent (20%): The learner's stated goal (e.g., "Become an AI PM" indicates high intent if aligned with the program's offerings).
    4. Budget (10%): Financial capability (company or self-funded). Higher weight for self-funded individuals or those with confirmed company sponsorship.
    5. Past Touchpoints (5%): Number of past interactions. More touchpoints imply higher interest.
    
    QUALIFIED LEAD EXAMPLE:
    {json.dumps(example_qualified, indent=2)}
    
    NURTURE LEAD EXAMPLE:
    {json.dumps(example_nurture, indent=2)}
    
    NEW CUSTOMER TO EVALUATE:
    {json.dumps(customer, indent=2)}
    
    Calculate a score from 0-100 for this customer based on the rubrics. If the score is ≥ 70, classify as "Qualified", otherwise as "Nurture".
    Provide detailed reasoning explaining how you arrived at this score.
    
    Return your analysis in JSON format with these fields:
    {{
      "score": (number between 0-100),
      "reasoning": (detailed explanation of the score),
      "status": ("Qualified" or "Nurture")
    }}
    """
    
    # Make API call to Groq
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        # If no API key, use a simplified scoring mechanism
        return simplified_scoring(customer)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        llm_response = result["choices"][0]["message"]["content"]
        
        # Extract JSON from the response
        try:
            # Try to parse as JSON directly
            qualification_result = json.loads(llm_response)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the text
            import re
            json_match = re.search(r'({.*})', llm_response.replace('\n', ''), re.DOTALL)
            if json_match:
                qualification_result = json.loads(json_match.group(1))
            else:
                return simplified_scoring(customer)
                
        return qualification_result
        
    except Exception as e:
        print(f"Error calling Groq API: {str(e)}")
        return simplified_scoring(customer)

def simplified_scoring(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Simplified scoring mechanism as fallback"""
    score = 0
    reasoning_parts = []
    
    # Fit (40%)
    fit_score = 0
    if customer.get("goal") == "Become an AI PM":
        fit_score = 40
    elif customer.get("goal") and "AI" in customer.get("goal"):
        fit_score = 30
    elif customer.get("goal"):
        fit_score = 20
    reasoning_parts.append(f"Fit score: {fit_score}/40 based on goal: '{customer.get('goal')}'")
    
    # Engagement (25%)
    engagement_score = 0
    engaged_mins = customer.get("engaged_mins", 0)
    if engaged_mins >= 60:
        engagement_score = 25
    elif engaged_mins >= 30:
        engagement_score = 15
    elif engaged_mins > 0:
        engagement_score = (engaged_mins / 60) * 25
    
    if customer.get("asked_q"):
        engagement_score = min(25, engagement_score + 5)
    reasoning_parts.append(f"Engagement score: {engagement_score}/25 based on {engaged_mins} minutes and questions asked: {customer.get('asked_q')}")
    
    # Intent (20%)
    intent_score = 0
    if customer.get("goal") == "Become an AI PM":
        intent_score = 20
    elif customer.get("goal") and "AI" in customer.get("goal"):
        intent_score = 15
    elif customer.get("goal"):
        intent_score = 10
    reasoning_parts.append(f"Intent score: {intent_score}/20 based on stated goal")
    
    # Budget (10%)
    budget_score = 0
    if customer.get("budget") == "Self":
        budget_score = 10
    elif customer.get("budget") == "Company":
        budget_score = 8
    reasoning_parts.append(f"Budget score: {budget_score}/10 based on {customer.get('budget')} funding")
    
    # Past Touchpoints (5%)
    touchpoints_score = min(5, customer.get("past_touchpoints", 0))
    reasoning_parts.append(f"Touchpoints score: {touchpoints_score}/5 based on {customer.get('past_touchpoints')} previous interactions")
    
    # Total score
    total_score = fit_score + engagement_score + intent_score + budget_score + touchpoints_score
    status = "Qualified" if total_score >= 70 else "Nurture"
    
    reasoning = f"Total score: {total_score}/100. " + " ".join(reasoning_parts)
    
    return {
        "score": total_score,
        "reasoning": reasoning,
        "status": status
    }

@app.post("/customers/{id}/qualify", response_model=Customer)
def qualify_customer(id: int):
    """Qualify a customer as a lead"""
    customers_list = read_customers_from_csv()
    
    for i, customer in enumerate(customers_list):
        if customer.id == id:
            # Calculate engaged minutes if not already calculated
            if not customer.engaged_mins and customer.webinar_join and customer.webinar_leave:
                customer.engaged_mins = calculate_engaged_minutes(customer)
            
            # Convert to dict for processing
            customer_dict = customer.dict()
            
            # Format datetime objects for JSON
            for key in ["webinar_join", "webinar_leave"]:
                if customer_dict.get(key):
                    customer_dict[key] = customer_dict[key].isoformat()
            
            # Get qualification result from LLM
            qualification = qualify_lead_with_llm(customer_dict)
            
            # Update customer with qualification results
            customer.score = qualification.get("score")
            customer.reasoning = qualification.get("reasoning")
            customer.status = qualification.get("status")
            
            # Save updated customer to CSV
            customers_list[i] = customer
            write_customers_to_csv(customers_list)
            
            return customer
    
    raise HTTPException(status_code=404, detail="Customer not found")

