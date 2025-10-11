#!/usr/bin/env python3
"""
Test script to verify Supabase connection and basic operations
"""

import os
from dotenv import load_dotenv
from supabase_service import SupabaseService

def test_supabase_connection():
    """Test basic Supabase connection and operations"""
    print("Testing Supabase connection...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if environment variables are set
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables are required")
            print("Please create a .env file with your Supabase credentials")
            return False
        
        print(f"✅ Environment variables loaded")
        print(f"   SUPABASE_URL: {supabase_url[:20]}...")
        print(f"   SUPABASE_KEY: {supabase_key[:20]}...")
        
        # Initialize Supabase service
        service = SupabaseService()
        print("✅ Supabase service initialized")
        
        # Test basic connection by fetching customers
        customers = service.get_customers()
        print(f"✅ Connection successful! Found {len(customers)} customers in database")
        
        # Test creating a test customer
        test_customer = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "country": "Test Country",
            "goal": "Test Goal",
            "budget": "Self",
            "asked_q": True,
            "referred": False,
            "past_touchpoints": 1
        }
        
        print("Testing customer creation...")
        created_customer = service.create_customer(test_customer)
        print(f"✅ Test customer created with ID: {created_customer['id']}")
        
        # Test updating the customer
        print("Testing customer update...")
        test_customer["goal"] = "Updated Test Goal"
        updated_customer = service.update_customer(created_customer['id'], test_customer)
        print(f"✅ Test customer updated: {updated_customer['goal']}")
        
        # Test qualifying the customer
        print("Testing customer qualification...")
        qualified_customer = service.qualify_customer(created_customer['id'])
        print(f"✅ Test customer qualified with score: {qualified_customer.get('score', 'N/A')}")
        
        # Test deleting the customer
        print("Testing customer deletion...")
        delete_result = service.delete_customer(created_customer['id'])
        if delete_result:
            print("✅ Test customer deleted successfully")
        else:
            print("❌ Failed to delete test customer")
        
        print("\n🎉 All tests passed! Supabase integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your .env file has the correct SUPABASE_URL and SUPABASE_KEY")
        print("2. Verify that the customers table exists in your Supabase database")
        print("3. Check that your Supabase project is active and accessible")
        print("4. Run the migration script to create the customers table")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    exit(0 if success else 1)

