from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Header
from datetime import datetime
import requests
import json
import os
from enum import Enum
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

app = FastAPI()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Verify the JWT token with Supabase
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

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

#Create
@app.post("/customers", response_model=Customer)
async def create_customer(customer: Customer, current_user = Depends(get_current_user)):
    # Calculate engaged minutes if not already calculated
    if not customer.engaged_mins and customer.webinar_join and customer.webinar_leave:
        customer.engaged_mins = calculate_engaged_minutes(customer)
    
    # Convert customer to dict for Supabase
    customer_dict = customer.model_dump()
    
    # Format datetime objects for JSON
    for key in ["webinar_join", "webinar_leave"]:
        if customer_dict.get(key):
            customer_dict[key] = customer_dict[key].isoformat()
    
    # Insert into Supabase
    result = supabase.table("customers").insert(customer_dict).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create customer")
    
    # Then qualify the customer
    return qualify_customer(customer.id)

#Read
@app.get("/customers", response_model=List[Customer])
async def get_customers(current_user = Depends(get_current_user)):
    result = supabase.table("customers").select("*").execute()
    return result.data

#Update
@app.put("/customers/{id}", response_model=Customer)
async def update_customer(id: int, customer: Customer, current_user = Depends(get_current_user)):
    # Convert customer to dict for Supabase
    customer_dict = customer.model_dump()
    
    # Format datetime objects for JSON
    for key in ["webinar_join", "webinar_leave"]:
        if customer_dict.get(key):
            customer_dict[key] = customer_dict[key].isoformat()
    
    result = supabase.table("customers").update(customer_dict).eq("id", id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return result.data[0]

#Delete
@app.delete("/customers/{id}", response_model=Customer)
async def delete_customer(id: int, current_user = Depends(get_current_user)):
    result = supabase.table("customers").delete().eq("id", id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return result.data[0]

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
async def qualify_customer(id: int, current_user = Depends(get_current_user)):
    """Qualify a customer as a lead"""
    # Get customer from Supabase
    result = supabase.table("customers").select("*").eq("id", id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_data = result.data[0]
    
    # Calculate engaged minutes if not already calculated
    if not customer_data.get("engaged_mins") and customer_data.get("webinar_join") and customer_data.get("webinar_leave"):
        customer_data["engaged_mins"] = calculate_engaged_minutes(Customer(**customer_data))
    
    # Get qualification result from LLM
    qualification = qualify_lead_with_llm(customer_data)
    
    # Update customer with qualification results
    update_data = {
        "score": qualification.get("score"),
        "reasoning": qualification.get("reasoning"),
        "status": qualification.get("status")
    }
    
    result = supabase.table("customers").update(update_data).eq("id", id).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update customer qualification")
    
    return Customer(**result.data[0])

# Add authentication endpoints
class AuthRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/signup")
async def signup(auth_data: AuthRequest):
    try:
        response = supabase.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password
        })
        return {"message": "Signup successful", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(auth_data: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth_data.email,
            "password": auth_data.password
        })
        return {
            "message": "Login successful",
            "access_token": response.session.access_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/logout")
async def logout(current_user = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

