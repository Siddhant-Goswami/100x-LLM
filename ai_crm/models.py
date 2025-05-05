from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr

class BudgetType(str, Enum):
    COMPANY = "company"
    SELF = "self"

class CustomerStatus(str, Enum):
    SQL = "SQL"
    NURTURE = "Nurture"

class Customer(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    title: str
    goal: str
    budget: BudgetType
    country: str
    webinar_join: Optional[datetime] = None
    webinar_leave: Optional[datetime] = None
    engaged_mins: Optional[int] = None
    asked_question: bool = False
    score: Optional[int] = None
    reasoning: Optional[str] = None
    status: Optional[CustomerStatus] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    @property
    def is_qualified(self) -> bool:
        """Returns True if the customer is sales qualified (score >= 70)"""
        return self.score is not None and self.score >= 70

class CustomerQualificationResponse(BaseModel):
    score: int
    reasoning: str 