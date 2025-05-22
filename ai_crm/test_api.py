import requests
from datetime import datetime, timedelta
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_create_customer():
    print("\n1. Testing Create Customer...")
    
    # Sample customer data
    customer_data = {
        "id": 1,  # This will be overridden by SERIAL in database
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "country": "India",
        "goal": "Become an AI PM",
        "budget": "Self",
        "webinar_join": (datetime.now() - timedelta(hours=2)).isoformat(),
        "webinar_leave": (datetime.now() - timedelta(hours=1)).isoformat(),
        "asked_q": True,
        "referred": False,
        "past_touchpoints": 3
    }
    
    response = requests.post(f"{BASE_URL}/customers", json=customer_data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Customer created successfully!")
        print("Response:", json.dumps(response.json(), indent=2))
        return response.json()["id"]
    else:
        print("Error creating customer:", response.text)
        return None

def test_get_customers():
    print("\n2. Testing Get All Customers...")
    response = requests.get(f"{BASE_URL}/customers")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        customers = response.json()
        print(f"Found {len(customers)} customers")
        print("First customer:", json.dumps(customers[0], indent=2) if customers else "No customers")
    else:
        print("Error getting customers:", response.text)

def test_update_customer(customer_id):
    print("\n3. Testing Update Customer...")
    
    # Updated customer data
    update_data = {
        "id": customer_id,
        "name": "Updated Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "country": "USA",
        "goal": "Become an AI PM",
        "budget": "Company",
        "webinar_join": (datetime.now() - timedelta(hours=2)).isoformat(),
        "webinar_leave": (datetime.now() - timedelta(hours=1)).isoformat(),
        "asked_q": True,
        "referred": True,
        "past_touchpoints": 5
    }
    
    response = requests.put(f"{BASE_URL}/customers/{customer_id}", json=update_data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Customer updated successfully!")
        print("Updated customer:", json.dumps(response.json(), indent=2))
    else:
        print("Error updating customer:", response.text)

def test_qualify_customer(customer_id):
    print("\n4. Testing Qualify Customer...")
    response = requests.post(f"{BASE_URL}/customers/{customer_id}/qualify")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Customer qualified successfully!")
        print("Qualification result:", json.dumps(response.json(), indent=2))
    else:
        print("Error qualifying customer:", response.text)

def test_delete_customer(customer_id):
    print("\n5. Testing Delete Customer...")
    response = requests.delete(f"{BASE_URL}/customers/{customer_id}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Customer deleted successfully!")
        print("Deleted customer:", json.dumps(response.json(), indent=2))
    else:
        print("Error deleting customer:", response.text)

def run_all_tests():
    print("Starting API Tests...")
    
    # Create a customer and get its ID
    customer_id = test_create_customer()
    if customer_id:
        # Run other tests
        test_get_customers()
        test_update_customer(customer_id)
        test_qualify_customer(customer_id)
        test_delete_customer(customer_id)
        
        # Verify deletion by getting all customers again
        print("\nVerifying deletion...")
        test_get_customers()
    else:
        print("Could not proceed with tests as customer creation failed")

if __name__ == "__main__":
    run_all_tests() 