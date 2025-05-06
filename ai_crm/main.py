from typing import List, Optional
from fastapi import FastAPI, HTTPException
from ai_crm.models import Customer, CustomerQualificationResponse
from ai_crm.services import qualify_customer
from ai_crm.database import init_db, get_all_customers, get_customer_by_id, save_customer, delete_customer

app = FastAPI()

# Initialize the database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/customers", response_model=Customer)
async def create_customer(customer: Customer):
    """Create a new customer and automatically qualify it."""
    # Qualify the customer
    qualified_customer = await qualify_customer(customer)
    
    # Store the customer
    return save_customer(qualified_customer)

@app.get("/customers", response_model=List[Customer])
async def get_customers():
    """Get all customers."""
    return get_all_customers()

@app.get("/customers/qualified", response_model=List[Customer])
async def get_qualified_customers_endpoint():
    """Get all sales qualified customers (score >= 70)."""
    return [customer for customer in get_all_customers() if customer.is_qualified]

@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int):
    """Get a specific customer by ID."""
    customer = get_customer_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: int, customer: Customer):
    """Update a customer and re-qualify it."""
    existing_customer = get_customer_by_id(customer_id)
    if existing_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Preserve the ID
    customer.id = customer_id
    # Re-qualify the customer
    qualified_customer = await qualify_customer(customer)
    return save_customer(qualified_customer)

@app.delete("/customers/{customer_id}", response_model=Customer)
async def delete_customer_endpoint(customer_id: int):
    """Delete a customer."""
    deleted_customer = delete_customer(customer_id)
    if deleted_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return deleted_customer

