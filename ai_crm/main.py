from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_crm.repository import init_db
from ai_crm.api import customers_router

app = FastAPI(
    title="AI-CRM API",
    description="API for AI-powered customer relationship management",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers_router)

# Initialize the database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "online", "message": "AI-CRM API is running"}

