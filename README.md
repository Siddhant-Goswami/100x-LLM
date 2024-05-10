# Project Documentation

## Overview
This project has all the code discussed in the 100x LLM lectures

## Installation Guide

## Creating a Virtual Environment (using venv, you can use conda or other virtual env packages as well)

1. Install `virtualenv` if not already installed:

```python
   pip install virtualenv
```
2. Create a new virtual environment:

```python
   virtualenv venv
   source venv/bin/activate
```

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd <project-directory>
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env_example` to `.env`.
   - Add necessary API keys and configuration settings to `.env`.

## Usage

### Chat Completions
- **OpenAI Chat Completions**: Utilizes OpenAI's GPT models for generating chat completions.
- **Groq Chat Completions**: Uses Groq's API for chat completions.
- **Hugging Face Chat Completions**: Demonstrates chat completions using Hugging Face models.

### Function Calling
- **Weather Information**: Fetches current weather using OpenAI and Groq APIs.
- **Stock Prices**: Retrieves current stock prices using OpenAI's API.

### Image Classification
- Utilizes Hugging Face's Inference API to classify images provided via URLs.

### Data Retrieval
- Custom API built with FastAPI to perform operations like adding numbers and querying data.

## File Structure
- `chat_completions/`: Contains scripts for chat completions using different APIs.
- `function_calling/`: Scripts for calling functions like fetching weather and stock prices.
- `huggingface/`: Examples of using Hugging Face's Inference API for tasks like image classification.
- `api/`: Contains FastAPI applications for custom functionalities.
- `data/`: Sample data files used in the project.

## Additional Notes
- Ensure that all environment variables are correctly set in the `.env` file before running the scripts.
- Refer to the respective API documentation for detailed usage and limitations:
  - [OpenAI Documentation](https://platform.openai.com/docs/guides/function-calling)
  - [Groq Documentation](https://console.groq.com/docs/quickstart)
  - [Hugging Face Models](https://huggingface.co/models)

## Contributing
Contributions to the project are welcome. Please ensure to follow the coding standards and submit pull requests for any new features or bug fixes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.