# AI-CRM: Lead Qualification System

An AI-powered CRM system that automatically qualifies sales leads based on multiple factors.

## Project Structure

The project follows a clean architecture with separation of concerns:

```
ai-crm/
├── ai_crm/                # Backend package
│   ├── api/               # FastAPI routers
│   ├── models.py          # Pydantic domain models
│   ├── repository/        # CSV data access layer
│   ├── services/          # Business logic (qualification)
│   └── main.py            # FastAPI application
│
└── frontend/              # Streamlit frontend
    ├── components/        # Reusable UI components
    ├── api.py             # Backend API client
    └── streamlit_app.py   # Main Streamlit application
```

## Technology Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Data Store**: CSV file
- **AI Provider**: Groq (LLaMA model for lead qualification)

## Key Features

- Thread-safe CSV database with proper locking
- Separation of concerns (repository, services, API, UI)
- Async API and API client for non-blocking I/O
- Typed data models with Pydantic
- Environment-driven configuration
- Modular UI components in Streamlit
- REST API with proper HTTP semantics

## Getting Started

### Prerequisites

- Python 3.10+
- A Groq API key (for AI-powered qualification)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-crm.git
   cd ai-crm
   ```

2. Set up environment variables:
   ```bash
   echo "GROQ_API_KEY=your_groq_api_key" > .env
   ```

3. Install backend dependencies:
   ```bash
   cd ai_crm
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd ai_crm
   uvicorn ai_crm.main:app --reload
   ```

2. Start the Streamlit frontend:
   ```bash
   cd frontend
   streamlit run streamlit_app.py
   ```

3. Access the applications:
   - Backend API: http://localhost:8000/docs
   - Frontend: http://localhost:8501

## Development

### API Documentation

The API documentation is available at `/docs` when the server is running. It includes all endpoints with request/response models and examples.

### Project Principles

This project follows these key principles:

1. **Domain-driven design**: Modeling based on the business domain
2. **Single responsibility**: Each component has a clear and focused purpose
3. **Type safety**: Using Pydantic models and type annotations
4. **Separation of concerns**: Repository for data access, services for business logic
5. **Async-first**: Non-blocking IO for better performance

## License

MIT
