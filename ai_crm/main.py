from typing import List, Optional
from fastapi import FastAPI, HTTPException
from ai_crm.models import Customer, CustomerQualificationResponse
from ai_crm.services import qualify_customer

app = FastAPI()

# Single in-memory storage for all customers
customers_list = []

# Helper function to get qualified customers
def get_qualified_customers():
    return [customer for customer in customers_list if customer.is_qualified]

@app.post("/customers", response_model=Customer)
async def create_customer(customer: Customer):
    """Create a new customer and automatically qualify it."""
    # Generate a new ID
    customer.id = len(customers_list) + 1
    
    # Qualify the customer
    qualified_customer = await qualify_customer(customer)
    
    # Store the customer
    customers_list.append(qualified_customer)
    return qualified_customer

@app.get("/customers", response_model=List[Customer])
async def get_customers():
    """Get all customers."""
    return customers_list

@app.get("/customers/qualified", response_model=List[Customer])
async def get_qualified_customers_endpoint():
    """Get all sales qualified customers (score >= 70)."""
    return get_qualified_customers()

@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int):
    """Get a specific customer by ID."""
    for customer in customers_list:
        if customer.id == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")

@app.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: int, customer: Customer):
    """Update a customer and re-qualify it."""
    for i, existing_customer in enumerate(customers_list):
        if existing_customer.id == customer_id:
            # Preserve the ID
            customer.id = customer_id
            # Re-qualify the customer
            qualified_customer = await qualify_customer(customer)
            customers_list[i] = qualified_customer
            return qualified_customer
    raise HTTPException(status_code=404, detail="Customer not found")

@app.delete("/customers/{customer_id}", response_model=Customer)
async def delete_customer(customer_id: int):
    """Delete a customer."""
    for i, customer in enumerate(customers_list):
        if customer.id == customer_id:
            deleted_customer = customers_list.pop(i)
            return deleted_customer
    raise HTTPException(status_code=404, detail="Customer not found")

