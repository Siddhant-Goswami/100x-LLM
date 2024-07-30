## Project Overview
This project has all the code discussed in the 100x LLM lectures

# Groq Chatbot and FastAPI Example

This repository contains two main components:
1. A FastAPI application that provides a simple addition API.
2. A Gradio-based chatbot interface powered by Groq.

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- An API key for Groq (set as an environment variable `GROQ_API_KEY`)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/your-repo.git
    cd your-repo
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required libraries:**
    ```sh
    pip install -r requirements.txt
    ```

### Running the FastAPI Application

1. **Navigate to the `api` directory:**
    ```sh
    cd api
    ```

2. **Run the FastAPI server:**
    ```sh
    uvicorn api:app --reload
    ```

   The API will be available at `http://127.0.0.1:8000`.

### Running the Gradio Chatbot

1. **Navigate to the `api` directory:**
    ```sh
    cd api
    ```

2. **Run the Gradio interface:**
    ```sh
    python groq_sdk_chatbot.py
    ```

   The Gradio interface will launch and provide a URL to access the chatbot.

## Usage

### FastAPI Addition API

- **Endpoint:** `POST /add`
- **Request Body:**
    ```json
    {
        "x": 1,
        "y": 2
    }
    ```
- **Response:**
    ```json
    {
        "result": 3
    }
    ```

### Gradio Chatbot

- Open the provided URL in your browser.
- Interact with the Groq-powered chatbot by typing your questions.


