from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 1. Define the blueprint for APIs
class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

# 2. Create the API endpoint

customers_list = []
#Create
@app.post("/customers", response_model=Customer)
def create_customer(customer: Customer):
    customers_list.append(customer)
    return customer

#Read
@app.get("/customers", response_model=List[Customer])
def get_customers():
    return customers_list

#Update
@app.put("/customers/{id}", response_model=Customer)
def update_customer(id: int, customer: Customer):
    for i, existing_customer in enumerate(customers_list):
        if existing_customer.id == id:
            customers_list[i] = customer
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")

#Delete
@app.delete("/customers/{id}", response_model=Customer)
def delete_customer(id: int):
    for i, customer in enumerate(customers_list):
        if customer.id == id:
            deleted_customer = customers_list.pop(i)
            return deleted_customer
    raise HTTPException(status_code=404, detail="Customer not found")

