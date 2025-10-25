from fastapi import FastAPI
import gradio as gr
from pydantic import BaseModel

app = FastAPI()

class Numbers(BaseModel):
    num1: float
    num2: float

@app.post("/add")
async def add_numbers(numbers: Numbers):
    result = numbers.num1 + numbers.num2
    return {"sum": result}

def greet(name):
    return f"Hello, {name}!"

gradio_app = gr.Interface(fn=greet, inputs="text", outputs="text")

app = gr.mount_gradio_app(app, gradio_app, path="/gradio")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI and Gradio app!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)