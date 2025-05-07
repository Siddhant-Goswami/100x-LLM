import os
import httpx
from typing import List, Dict, Any, Optional

# Base URL can be configured via environment variable
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class ApiClient:
    """API client for interacting with the backend."""
    
    @staticmethod
    async def get_customers() -> List[Dict[str, Any]]:
        """Get all customers from the API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/customers")
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def get_qualified_customers() -> List[Dict[str, Any]]:
        """Get qualified customers from the API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/customers/qualified")
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def get_customer(customer_id: int) -> Dict[str, Any]:
        """Get a specific customer by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/customers/{customer_id}")
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def create_customer(customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/customers", json=customer_data)
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def update_customer(customer_id: int, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing customer."""
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{BASE_URL}/customers/{customer_id}", json=customer_data)
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def delete_customer(customer_id: int) -> Dict[str, Any]:
        """Delete a customer."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{BASE_URL}/customers/{customer_id}")
            response.raise_for_status()
            return response.json() 