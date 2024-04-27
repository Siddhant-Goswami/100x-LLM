# Installation Guide and File Overview

## Creating a Virtual Environment

### Steps to Create a New Virtual Environment (using venv, you can use conda or other virtual env packages as well)

1. Install `virtualenv` if not already installed:

```python
   pip install virtualenv
```
2. Create a new virtual environment:

```python
   virtualenv venv
   source venv/bin/activate
```

## Installation Guide
1. Install the required packages listed in `requirements.txt`.
2. Copy the `.env_example` file and rename it to `.env`.
2. Add your API keys in the `.env` file.

## File Overview

### `GPT_function_call.py`
- Calls OpenAI API to get the current weather using a defined function.
- Demonstrates how to define functions for use in the request.
- Uses the GPT-3.5-turbo model for chat completions.

### `groq_function_call.py`
- Calls Groq API to get the current weather using a defined function.
- Demonstrates how to define functions for the request.
- Utilizes the mixtral-8x7b-32768 model for chat completions.

### `groq_chat_completions.py`
- Utilizes Groq API for chat completions.
- Demonstrates a basic chat completion request using the mixtral-8x7b-32768 model.

## Additional Notes
- Ensure API keys are set up correctly for OpenAI and Groq in the respective files.
- Follow the code comments for guidance on function definitions and API usage.

Groq docs: https://console.groq.com/docs/quickstart
OpenAI docs: https://platform.openai.com/docs/guides/function-calling