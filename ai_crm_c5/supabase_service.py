from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import requests
import os
from config import supabase

class SupabaseService:
    """Service class for handling Supabase operations"""
    
    def __init__(self):
        self.supabase = supabase
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer in Supabase"""
        try:
            # Calculate engaged minutes if webinar times are provided
            if customer_data.get('webinar_join') and customer_data.get('webinar_leave'):
                customer_data['engaged_mins'] = self._calculate_engaged_minutes(
                    customer_data['webinar_join'], 
                    customer_data['webinar_leave']
                )
            
            # Format datetime objects for JSON
            for key in ["webinar_join", "webinar_leave"]:
                if customer_data.get(key) and isinstance(customer_data[key], datetime):
                    customer_data[key] = customer_data[key].isoformat()
            
            result = self.supabase.table("customers").insert(customer_data).execute()
            
            if not result.data:
                raise Exception("Failed to create customer")
            
            return result.data[0]
        except Exception as e:
            raise Exception(f"Error creating customer: {str(e)}")
    
    def get_customers(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all customers from Supabase with optional status filter"""
        try:
            query = self.supabase.table("customers").select("*")
            
            if status_filter and status_filter != "All":
                query = query.eq("status", status_filter)
            
            result = query.execute()
            return result.data
        except Exception as e:
            raise Exception(f"Error fetching customers: {str(e)}")
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific customer by ID"""
        try:
            result = self.supabase.table("customers").select("*").eq("id", customer_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error fetching customer: {str(e)}")
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing customer"""
        try:
            # Calculate engaged minutes if webinar times are provided
            if customer_data.get('webinar_join') and customer_data.get('webinar_leave'):
                customer_data['engaged_mins'] = self._calculate_engaged_minutes(
                    customer_data['webinar_join'], 
                    customer_data['webinar_leave']
                )
            
            # Format datetime objects for JSON
            for key in ["webinar_join", "webinar_leave"]:
                if customer_data.get(key) and isinstance(customer_data[key], datetime):
                    customer_data[key] = customer_data[key].isoformat()
            
            result = self.supabase.table("customers").update(customer_data).eq("id", customer_id).execute()
            
            if not result.data:
                raise Exception("Customer not found")
            
            return result.data[0]
        except Exception as e:
            raise Exception(f"Error updating customer: {str(e)}")
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer"""
        try:
            result = self.supabase.table("customers").delete().eq("id", customer_id).execute()
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting customer: {str(e)}")
    
    def qualify_customer(self, customer_id: int) -> Dict[str, Any]:
        """Qualify a customer using LLM"""
        try:
            # Get customer data
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                raise Exception("Customer not found")
            
            # Calculate engaged minutes if not already calculated
            if not customer.get("engaged_mins") and customer.get("webinar_join") and customer.get("webinar_leave"):
                customer["engaged_mins"] = self._calculate_engaged_minutes(
                    customer["webinar_join"], 
                    customer["webinar_leave"]
                )
            
            # Get qualification result from LLM
            qualification = self._qualify_lead_with_llm(customer)
            
            # Update customer with qualification results
            update_data = {
                "score": qualification.get("score"),
                "reasoning": qualification.get("reasoning"),
                "status": qualification.get("status")
            }
            
            result = self.supabase.table("customers").update(update_data).eq("id", customer_id).execute()
            
            if not result.data:
                raise Exception("Failed to update customer qualification")
            
            return result.data[0]
        except Exception as e:
            raise Exception(f"Error qualifying customer: {str(e)}")
    
    def _calculate_engaged_minutes(self, webinar_join: str, webinar_leave: str) -> float:
        """Calculate engaged minutes from webinar join and leave times"""
        try:
            if isinstance(webinar_join, str):
                join_dt = datetime.fromisoformat(webinar_join.replace('Z', '+00:00'))
            else:
                join_dt = webinar_join
                
            if isinstance(webinar_leave, str):
                leave_dt = datetime.fromisoformat(webinar_leave.replace('Z', '+00:00'))
            else:
                leave_dt = webinar_leave
            
            engaged_time = (leave_dt - join_dt).total_seconds() / 60
            return round(engaged_time, 2)
        except Exception:
            return 0.0
    
    def _qualify_lead_with_llm(self, customer: Dict[str, Any]) -> Dict[str, Any]:
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
            return self._simplified_scoring(customer)
        
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
                    return self._simplified_scoring(customer)
                    
            return qualification_result
            
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            return self._simplified_scoring(customer)
    
    def _simplified_scoring(self, customer: Dict[str, Any]) -> Dict[str, Any]:
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

