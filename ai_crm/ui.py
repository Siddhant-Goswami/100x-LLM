import streamlit as st
import requests
from typing import List, Optional

# API base URL
BASE_URL = "http://localhost:8000"

# Initialize session state for customers list
if 'customers' not in st.session_state:
    st.session_state.customers = []

def fetch_customers():
    """Fetch all customers from the API"""
    try:
        response = requests.get(f"{BASE_URL}/customers")
        if response.status_code == 200:
            st.session_state.customers = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching customers: {str(e)}")

def create_customer(name: str, email: str, phone: Optional[str] = None, address: Optional[str] = None):
    """Create a new customer"""
    try:
        # Find the next available ID
        next_id = max([c['id'] for c in st.session_state.customers], default=0) + 1
        
        customer_data = {
            "id": next_id,
            "name": name,
            "email": email,
            "phone": phone,
            "address": address
        }
        
        response = requests.post(f"{BASE_URL}/customers", json=customer_data)
        if response.status_code == 200:
            st.success("Customer created successfully!")
            fetch_customers()
        else:
            st.error(f"Error creating customer: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating customer: {str(e)}")

def update_customer(customer_id: int, name: str, email: str, phone: Optional[str] = None, address: Optional[str] = None):
    """Update an existing customer"""
    try:
        customer_data = {
            "id": customer_id,
            "name": name,
            "email": email,
            "phone": phone,
            "address": address
        }
        
        response = requests.put(f"{BASE_URL}/customers/{customer_id}", json=customer_data)
        if response.status_code == 200:
            st.success("Customer updated successfully!")
            fetch_customers()
        else:
            st.error(f"Error updating customer: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating customer: {str(e)}")

def delete_customer(customer_id: int):
    """Delete a customer"""
    try:
        response = requests.delete(f"{BASE_URL}/customers/{customer_id}")
        if response.status_code == 200:
            st.success("Customer deleted successfully!")
            fetch_customers()
        else:
            st.error(f"Error deleting customer: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting customer: {str(e)}")

# Streamlit UI
st.title("Customer Management System")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose an operation", ["View Customers", "Add Customer", "Update Customer", "Delete Customer"])

# Fetch customers on initial load
fetch_customers()

if page == "View Customers":
    st.header("All Customers")
    if st.session_state.customers:
        for customer in st.session_state.customers:
            st.write(f"**ID:** {customer['id']}")
            st.write(f"**Name:** {customer['name']}")
            st.write(f"**Email:** {customer['email']}")
            if customer.get('phone'):
                st.write(f"**Phone:** {customer['phone']}")
            if customer.get('address'):
                st.write(f"**Address:** {customer['address']}")
            st.write("---")
    else:
        st.info("No customers found.")

elif page == "Add Customer":
    st.header("Add New Customer")
    with st.form("add_customer_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone (optional)")
        address = st.text_area("Address (optional)")
        
        submitted = st.form_submit_button("Add Customer")
        if submitted:
            if name and email:
                create_customer(name, email, phone, address)
            else:
                st.warning("Please fill in the required fields (Name and Email)")

elif page == "Update Customer":
    st.header("Update Customer")
    if st.session_state.customers:
        customer_id = st.selectbox(
            "Select Customer to Update",
            options=[c['id'] for c in st.session_state.customers]
        )
        
        # Get the selected customer's data
        selected_customer = next((c for c in st.session_state.customers if c['id'] == customer_id), None)
        
        if selected_customer:
            with st.form("update_customer_form"):
                name = st.text_input("Name", value=selected_customer['name'])
                email = st.text_input("Email", value=selected_customer['email'])
                phone = st.text_input("Phone", value=selected_customer.get('phone', ''))
                address = st.text_area("Address", value=selected_customer.get('address', ''))
                
                submitted = st.form_submit_button("Update Customer")
                if submitted:
                    if name and email:
                        update_customer(customer_id, name, email, phone, address)
                    else:
                        st.warning("Please fill in the required fields (Name and Email)")
    else:
        st.info("No customers available to update.")

elif page == "Delete Customer":
    st.header("Delete Customer")
    if st.session_state.customers:
        customer_id = st.selectbox(
            "Select Customer to Delete",
            options=[c['id'] for c in st.session_state.customers]
        )
        
        if st.button("Delete Customer"):
            delete_customer(customer_id)
    else:
        st.info("No customers available to delete.")