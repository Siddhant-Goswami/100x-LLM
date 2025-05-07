import pytest
from fastapi.testclient import TestClient
import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_crm.main import app
from ai_crm.repository.database import CSV_FILE

client = TestClient(app)

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    # Save the original CSV file path
    original_csv_path = CSV_FILE
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        temp_path = Path(tmp.name)
    
    # Patch the CSV_FILE constant
    import ai_crm.repository.database
    ai_crm.repository.database.CSV_FILE = temp_path
    
    # Initialize the database
    from ai_crm.repository import init_db
    init_db()
    
    yield
    
    # Clean up: restore original path and remove temp file
    ai_crm.repository.database.CSV_FILE = original_csv_path
    if temp_path.exists():
        temp_path.unlink()

def test_root_endpoint():
    """Test the root endpoint returns correct status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "AI-CRM API is running" in data["message"]

def test_create_customer(temp_csv_file, monkeypatch):
    """Test creating a new customer."""
    # Mock the qualify_customer function to avoid calling Groq
    async def mock_qualify(customer):
        customer.score = 85
        customer.reasoning = "Mocked qualification reasoning"
        return customer
    
    import ai_crm.services.qualify
    monkeypatch.setattr(ai_crm.services.qualify, "qualify_customer", mock_qualify)
    
    # Create a test customer
    customer_data = {
        "name": "Test Customer",
        "email": "test@example.com",
        "title": "CTO",
        "goal": "Implement AI",
        "budget": "company",
        "country": "US",
        "asked_question": True
    }
    
    response = client.post("/customers", json=customer_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Customer"
    assert data["score"] == 85
    assert data["is_qualified"] is True

def test_get_customers(temp_csv_file, monkeypatch):
    """Test getting all customers."""
    # First create a test customer (with mocked qualification)
    async def mock_qualify(customer):
        customer.score = 75
        customer.reasoning = "Mocked qualification"
        return customer
    
    import ai_crm.services.qualify
    monkeypatch.setattr(ai_crm.services.qualify, "qualify_customer", mock_qualify)
    
    # Create a test customer
    customer_data = {
        "name": "Test Customer",
        "email": "test@example.com",
        "title": "CTO",
        "goal": "Implement AI",
        "budget": "company",
        "country": "US"
    }
    
    client.post("/customers", json=customer_data)
    
    # Now test GET endpoint
    response = client.get("/customers")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Customer"
    assert data[0]["score"] == 75 