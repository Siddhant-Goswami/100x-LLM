from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

# Step 1: Define the blueprint for API request
class Numbers(BaseModel):
    x: int
    y: int

# Step 2: Creating an API endpoint
@app.post("/add")
def add_api(numbers: Numbers):
    return {"result": add_numbers(numbers.x, numbers.y)}



# logic 
def add_numbers(x, y):
    return x + y

print(add_numbers(2,2))