from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI()

security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "secret"
    if credentials.username == correct_username and credentials.password == correct_password:
        return credentials.username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )

class Numbers(BaseModel):
    x: int
    y: int

def add_numbers(x, y):
    return x + y

@app.post("/add/")
def add(numbers: Numbers, username: str = Depends(authenticate_user)):
    return {"result": add_numbers(numbers.x, numbers.y)}
