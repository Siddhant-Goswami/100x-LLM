# 100x Applied AI - Complete Learning Guide

Welcome to the 100x Applied AI repository! This is a comprehensive resource for learning and implementing  Large Language Model (LLM) & Agentic applications. Whether you're a complete beginner or looking to enhance your AI engineering skills, this guide will help you navigate through practical implementations.

## Table of Contents
- [What is this Repository?](#what-is-this-repository)
- [Who is this for?](#who-is-this-for)
- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [Repository Structure](#repository-structure)
- [Learning Path](#learning-path)
- [Example Projects](#example-projects)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## What is this Repository?

This repository contains **140+ practical implementations** from the 100x Applied AI cohort, covering:

- **Full-Stack AI Applications**: Build complete AI-powered applications
- **Prompt Engineering**: Master the art of communicating with AI models
- **Tool Calling**: Connect LLMs to external tools and APIs
- **RAG (Retrieval Augmented Generation)**: Build AI systems that can search and use your own data
- **LLM Workflows**: Learn how to orchestrate AI models for complex tasks
- **AI Agents**: Create autonomous AI systems that can reason and take actions

**Key Technologies**: OpenAI, Groq, Hugging Face, LlamaIndex, FastAPI, Streamlit

---

## Who is this for?

- **Beginners**: Each section includes detailed explanations and step-by-step guides
- **Developers**: Ready-to-use code snippets and API implementations
- **AI Enthusiasts**: Learn modern AI patterns and best practices

---

## Prerequisites

### Required Knowledge
- **Basic Python**: Understanding of functions, classes, and modules
- **Command Line**: Basic terminal/command prompt usage
- **APIs (Optional)**: Helpful but not required

### Required Software
- **Python 3.8 or higher** ([Download here](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** ([Download here](https://git-scm.com/downloads))
- **Text Editor** (VS Code, Cursor, PyCharm etc)

### Required API Keys
You'll need at least one of these (most have free tiers):
- **OpenAI API Key** ([Get it here](https://platform.openai.com/api-keys)) - Most examples use this
- **Groq API Key** ([Get it here](https://console.groq.com/)) - Free and fast alternative
- **Hugging Face Token** ([Get it here](https://huggingface.co/settings/tokens)) - For open-source models

---

## Quick Start Guide

### Step 1: Clone the Repository
```bash
# Open your terminal and run:
git clone https://github.com/Siddhant-Goswami/open-source-project.git
cd open-source-project
```

### Step 2: Set Up Python Environment
```bash
# Create a virtual environment (keeps dependencies isolated)
python -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal now
```

### Step 3: Install Dependencies
```bash
# Install all required packages (this may take a few minutes)
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
```bash
# Create your environment file
cp .env_example .env

# Open .env in your text editor and add your API keys:
# OPENAI_API_KEY=sk-your-key-here
# GROQ_API_KEY=your-groq-key-here
# HUGGINGFACE_API_KEY=your-hf-key-here
```

### Step 5: Test Your Setup
```bash
# Try running a simple example
python llm_workflows/prompt_chaining.py
```

If you see output without errors, congratulations! You're ready to start learning.

---

## Repository Structure

### 1. **Full-Stack Applications** (`llm_full_stack/`)
Complete applications combining AI with web interfaces. Start here to see how everything comes together!

**What you'll learn:**
- Building APIs with FastAPI
- Creating UIs with Streamlit and Gradio
- Authentication (Auth0 integration)
- Email integration
- Database management

**Available Apps:**
- `ai_crm/` - AI-powered Customer Relationship Management
- `auth/` - Authentication system
- `api/` - RESTful API examples

**Start here:** `llm_full_stack/api/app.py`

**Example use case:** Build a customer support chatbot with user authentication

---

### 2. **Prompt Engineering** (`prompts/`)
28 specialized prompt templates for different roles and use cases. Master the art of communicating with AI!

**Available Prompts:**
- `ai_cmo.md` - Chief Marketing Officer prompts
- `ai_cto.md` - Chief Technology Officer prompts
- `business_coach.md` - Business coaching prompts
- `product_manager.md` - Product management prompts
- `linkedin_content.md` - Social media content creation
- And 23 more specialized prompts!

**Start here:** Browse the `prompts/` directory

**Example use case:** Generate professional LinkedIn posts or get technical advice

---

### 3. **Tool Calling** (`tool_calling/`)
Connect LLMs to external tools, APIs, and databases to extend their capabilities.

**What you'll learn:**
- Defining functions that LLMs can call
- Handling function calls and responses
- Building tools for different providers (OpenAI, Groq, Llama)

**Start here:** `tool_calling/gpt_function_calling.py`

**Example use case:** Build a weather bot that can check real-time weather data

---

### 4. **RAG - Basic** (`rag/`)
Retrieval Augmented Generation lets AI models access and use your own documents.

**What you'll learn:**
- **Level 1**: Using OpenAI's File Search API (easiest)
- **Level 2**: LlamaIndex integration (more control)

**Start here:** `rag/openai_file_search.py`

**Example use case:** Build a chatbot that answers questions about your company's documentation

---

### 5. **RAG - Advanced** (`rag_advanced/`)
Build RAG systems from scratch with complete control over the retrieval process.

**What you'll learn:**
- Creating embeddings (vector representations of text)
- Storing vectors in Supabase
- Semantic search (finding similar content)
- Custom retrieval strategies

**Start here:** `rag_advanced/rag_from_scratch.py`

**Example use case:** Build a research assistant that searches through academic papers

---

### 6. **LLM Workflows** (`llm_workflows/`)
Learn how to chain multiple LLM calls together for complex, multi-step tasks.

**What you'll learn:**
- Prompt chaining: Breaking complex tasks into steps
- Router patterns: Directing requests to appropriate handlers
- Parallel processing: Running multiple AI tasks simultaneously
- Code review automation: Using AI to review code

**Start here:** `llm_workflows/prompt_chaining.py`

**Example use case:** Automatically generate marketing copy with brand consistency checks

---

### 7. **AI Agents** (`agents/`)
Autonomous AI systems that can reason, plan, and take actions to accomplish complex goals.

**What you'll learn:**
- **ReAct Pattern**: Reasoning + Acting loop (agents that think before acting)
- **Research Agents**: Agents that can search and analyze web content
- **Reflection Pattern**: Agents that improve through self-evaluation

**Available Agents:**
- `trip_planner/` - Plan complete trips with itineraries
- `job-posting/` - Generate and optimize job descriptions
- `react_patterns/` - Learn the ReAct reasoning framework

**Start here:** `agents/react_patterns/react_v0.py`

**Example use case:** Build a travel planning agent that researches destinations and creates itineraries

---

### 8. **Hugging Face Integration** (`huggingface/`)
Work with open-source models and the Hugging Face ecosystem.

**What you'll learn:**
- Using transformer models
- Image segmentation
- Chat completions with open-source models
- Model inference

**Start here:** `huggingface/chat_completion.py`

---

## Learning Path

### For Complete Beginners:
Follow this structured 6-week roadmap to go from zero to building AI applications:

1. **Week 1 - Prompt Engineering**: Start by exploring the `prompts/` directory to learn how to communicate effectively with AI models
2. **Week 2 - Full-Stack Applications**: Run `llm_full_stack/api/app.py` to see complete AI applications in action
3. **Week 3 - Tool Calling**: Try `tool_calling/gpt_function_calling.py` to learn how to extend LLM capabilities with external tools
4. **Week 4 - RAG Systems**: Build `rag/openai_file_search.py` to create AI that can search your own documents
5. **Week 5 - LLM Workflows**: Explore `llm_workflows/prompt_chaining.py` to orchestrate complex multi-step AI tasks
6. **Week 6 - AI Agents**: Build your first autonomous agent with `agents/react_patterns/react_v0.py`

### For Intermediate Developers:
Jump straight into building with this accelerated path:

1. **Full-Stack Applications**: Start with `llm_full_stack/api/app.py` to understand complete AI systems
2. **Prompt Engineering**: Master `prompts/` to optimize AI interactions
3. **Tool Calling**: Integrate external APIs with `tool_calling/gpt_function_calling.py`
4. **Advanced RAG**: Build custom retrieval systems with `rag_advanced/rag_from_scratch.py`
5. **LLM Workflows**: Create complex orchestrations in `llm_workflows/`
6. **Multi-Agent Systems**: Explore `agents/` for collaborative AI agents

### For Advanced Users:
Deep dive into advanced patterns and build production systems:

- **Full-Stack Integration**: Combine all patterns in `llm_full_stack/` with authentication and databases
- **Custom Workflows**: Build sophisticated orchestration in `llm_workflows/`
- **Advanced Agents**: Explore `agents/reflection.py` for self-improving agent patterns
- **Production RAG**: Implement enterprise-grade retrieval with `rag_advanced/` and Supabase
- **Multi-Agent Orchestration**: Build teams of specialized agents

---

## Example Projects

Start with these hands-on projects that follow the learning path:

### Project 1: Full-Stack AI API
```bash
# Navigate to full-stack directory
cd llm_full_stack/api

# Run the FastAPI + Gradio application
python app.py

# What this does:
# 1. Starts a FastAPI server with AI endpoints
# 2. Launches a Gradio UI for interaction
# 3. Shows how to integrate AI into web applications
```

### Project 2: Tool-Enabled Weather Bot
```bash
# Navigate to tool calling directory
cd tool_calling

# Run the GPT function calling example
python gpt_function_calling.py

# What this does:
# 1. Connects LLM to external weather API
# 2. Handles function calls dynamically
# 3. Returns real-time weather data through AI
```

### Project 3: Document Q&A with RAG
```bash
# Navigate to RAG directory
cd rag

# Run the OpenAI file search example
python openai_file_search.py

# What this does:
# 1. Uploads your documents to vector storage
# 2. Creates a searchable knowledge base
# 3. Answers questions using your own data
```

### Project 4: Marketing Copy Generator
```bash
# Navigate to workflows directory
cd llm_workflows

# Run the prompt chaining app
python prompt_chaining_app.py

# What this does:
# 1. Generates marketing copy with AI
# 2. Reviews and checks brand consistency
# 3. Optimizes content for engagement
```

### Project 5: AI Trip Planner Agent
```bash
# Navigate to agents directory
cd agents/trip_planner

# Run the autonomous trip planner
python main.py

# What this does:
# 1. Takes your destination and travel preferences
# 2. Researches activities, hotels, and restaurants
# 3. Creates a complete day-by-day itinerary
```

---

## Troubleshooting

### Issue: "Module not found" error
**Solution:**
```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "API key not found" error
**Solution:**
```bash
# Check your .env file exists
ls -la .env

# Make sure it contains your API keys
cat .env

# The format should be:
# OPENAI_API_KEY=sk-...
# No spaces around the = sign!
```

### Issue: "Rate limit exceeded"
**Solution:**
- You've hit your API quota
- Wait a few minutes or upgrade your API plan
- Try using Groq API (usually more generous free tier)

### Issue: "Connection timeout"
**Solution:**
- Check your internet connection
- Some corporate networks block API calls
- Try using a personal network or VPN

### Need more help?
- Check individual directory README files
- Review the code comments (they're detailed!)
- Open an issue on GitHub

---

## Environment Variables

Create a `.env` file in the root directory with the following:

```bash
# Required for most examples
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: For alternative LLM providers
GROQ_API_KEY=your-groq-key-here

# Optional: For Hugging Face models
HUGGINGFACE_API_KEY=your-huggingface-token-here

# Optional: For RAG with Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# Optional: For Notion integration
NOTION_TOKEN=your-notion-token-here

# Optional: For Auth0
AUTH0_DOMAIN=your-auth0-domain
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
```

---

## Key Concepts Explained

### What is an LLM?
Large Language Model - AI trained on vast amounts of text that can understand and generate human-like text.

### What is RAG?
Retrieval Augmented Generation - Giving LLMs access to your specific documents/data so they can answer questions about your content.

### What is an AI Agent?
An autonomous system that can reason, plan, and take actions to accomplish goals (like a virtual assistant).

### What is Function Calling?
Allowing LLMs to use external tools, APIs, and databases to get real-time information or take actions.

### What is Prompt Engineering?
The art and science of crafting instructions (prompts) to get the best results from AI models.

---

## Technologies Used

| Technology | Purpose | Learn More |
|------------|---------|------------|
| **OpenAI** | GPT models for text generation | [docs.openai.com](https://platform.openai.com/docs) |
| **Groq** | Fast inference for LLMs | [console.groq.com](https://console.groq.com) |
| **LlamaIndex** | RAG framework | [docs.llamaindex.ai](https://docs.llamaindex.ai) |
| **FastAPI** | Modern Python web framework | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| **Streamlit** | Data app framework | [streamlit.io](https://streamlit.io) |
| **Supabase** | Database and vector storage | [supabase.com](https://supabase.com) |

---

## Next Steps

1. **Pick a project** from the Example Projects section
2. **Follow the code** - Each file has detailed comments
3. **Modify and experiment** - Change prompts, try different models
4. **Build something new** - Combine different patterns
5. **Share your work** - Contribute back to the community!

---

## Contributing

We welcome contributions! Here's how:

1. **Fork the repository** (click "Fork" button on GitHub)
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit
   ```bash
   git commit -m "Add: Description of your changes"
   ```
4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub

### Contribution Ideas:
- Add more examples
- Improve documentation
- Fix bugs
- Add tests
- Create tutorial videos

---

## License

This project is open-source. Check the LICENSE file for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/Siddhant-Goswami/open-source-project/issues)
- **Discussions**: Use GitHub Discussions for questions
- **Updates**: Watch the repository for updates

---

Built with ❤️ for 100xEngineers, by 100xEngineers.

