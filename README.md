# 100x Applied AI - Code Snippets

This repository contains code snippets and examples from the 100x Applied AI cohort lectures. It demonstrates various practical implementations of LLM-based applications and patterns.

## Project Overview

The repository includes implementations of:
- LLM Workflows and Patterns
- RAG (Retrieval Augmented Generation)
- Agentic Patterns
- Chat Completions with various providers
- Function Calling
- And more...

## Installation Guide

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Environment setup:
   - Copy `.env_example` to `.env`
   - Add your API keys and configurations

## Repository Structure

### Core Components

#### LLM Workflows (`llm_workflows/`)
- Prompt Chaining and Orchestration
- Router-based Workflows
- Parallel Processing Patterns
- Code Review Automation
- Evaluation and Optimization

#### RAG Implementations (`rag/` & `rag2/`)
- Different approaches to Retrieval Augmented Generation
- Integration examples

#### Agentic Patterns (`agentic_patterns/`)
- Implementation of various AI agent patterns
- Agent orchestration examples

#### Chat Completions (`chat_completions/`)
- OpenAI integration
- Groq implementation
- Other LLM providers

#### Function Calling (`function_calling/`)
- Examples of function calling with LLMs
- Real-world use cases

#### Hugging Face Integration (`huggingface/`)
- Model usage examples
- Inference API implementations

#### Additional Components
- `agents/`: Various agent implementations
- `presentation_generator/`: Automated presentation creation
- `notion_data_integration/`: Notion API integration examples
- `api/`: FastAPI-based endpoints
- `auth/`: Authentication implementations
- `langchain/`: LangChain usage examples

## Usage

Each directory contains specific examples and implementations. Refer to individual README files within each directory for detailed usage instructions.

## Additional Resources

- Check the `prompts/` directory for various prompt engineering examples
- See `llm_workflows/README.md` for detailed workflow patterns
- Explore individual directories for specific implementation details

## Environment Variables

Required environment variables (add to `.env`):
- OpenAI API keys
- Hugging Face API tokens
- Other provider credentials as needed

## Contributing

Feel free to contribute by:
1. Forking the repository
2. Creating a feature branch
3. Submitting a pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Acknowledgments

This codebase is part of the 100x Applied AI cohort curriculum, demonstrating practical implementations of various LLM concepts and patterns.
