from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Numbers(BaseModel):
    x: int
    y: int

@app.post("/add/")
def add(numbers: Numbers):
    return {"result": add_numbers(numbers.x, numbers.y)}

def add_numbers(x, y):
    return x + y
