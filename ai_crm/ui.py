import streamlit as st
import requests
from typing import List, Optional
from datetime import datetime
from enum import Enum

# API base URL
BASE_URL = "http://localhost:8000"

# Define enums to match main.py
class Status(str, Enum):
    QUALIFIED = "Qualified"
    NURTURE = "Nurture"

class BudgetType(str, Enum):
    SELF = "Self"
    COMPANY = "Company"

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

def create_customer(name: str, email: str, phone: Optional[str] = None, country: Optional[str] = None,
                   goal: Optional[str] = None, budget: Optional[str] = None,
                   webinar_join: Optional[datetime] = None, webinar_leave: Optional[datetime] = None,
                   asked_q: bool = False, referred: bool = False, past_touchpoints: int = 0):
    """Create a new customer"""
    try:
        # Find the next available ID
        next_id = max([c['id'] for c in st.session_state.customers], default=0) + 1
        
        # If webinar_join is provided but not webinar_leave, set webinar_leave to 2 hours after join
        if webinar_join and not webinar_leave:
            webinar_leave = webinar_join + datetime.timedelta(hours=2)
        
        customer_data = {
            "id": next_id,
            "name": name,
            "email": email,
            "phone": phone,
            "country": country,
            "goal": goal,
            "budget": budget,
            "webinar_join": webinar_join.isoformat() if webinar_join else None,
            "webinar_leave": webinar_leave.isoformat() if webinar_leave else None,
            "asked_q": asked_q,
            "referred": referred,
            "past_touchpoints": past_touchpoints
        }
        
        response = requests.post(f"{BASE_URL}/customers", json=customer_data)
        if response.status_code == 200:
            st.success("Customer created successfully!")
            fetch_customers()
        else:
            st.error(f"Error creating customer: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating customer: {str(e)}")

def update_customer(customer_id: int, name: str, email: str, phone: Optional[str] = None, 
                   country: Optional[str] = None, goal: Optional[str] = None, 
                   budget: Optional[str] = None, webinar_join: Optional[datetime] = None, 
                   webinar_leave: Optional[datetime] = None, asked_q: bool = False, 
                   referred: bool = False, past_touchpoints: int = 0):
    """Update an existing customer"""
    try:
        # If webinar_join is provided but not webinar_leave, set webinar_leave to 2 hours after join
        if webinar_join and not webinar_leave:
            webinar_leave = webinar_join + datetime.timedelta(hours=2)
            
        customer_data = {
            "id": customer_id,
            "name": name,
            "email": email,
            "phone": phone,
            "country": country,
            "goal": goal,
            "budget": budget,
            "webinar_join": webinar_join.isoformat() if webinar_join else None,
            "webinar_leave": webinar_leave.isoformat() if webinar_leave else None,
            "asked_q": asked_q,
            "referred": referred,
            "past_touchpoints": past_touchpoints
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

def qualify_customer(customer_id: int):
    """Qualify a customer"""
    try:
        response = requests.post(f"{BASE_URL}/customers/{customer_id}/qualify")
        if response.status_code == 200:
            st.success("Customer qualification successful!")
            fetch_customers()
        else:
            st.error(f"Error qualifying customer: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error qualifying customer: {str(e)}")

# Streamlit UI
st.title("100xEngineers CRM")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose an operation", 
                          ["View Customers", "Add Customer", "Update Customer", "Delete Customer", "Qualify Customer"])

# Fetch customers on initial load
fetch_customers()

if page == "View Customers":
    st.header("All Customers")
    
    # Add filtering options
    filter_status = st.selectbox("Filter by Status", ["All", "Qualified", "Nurture"])
    
    filtered_customers = st.session_state.customers
    if filter_status != "All":
        filtered_customers = [c for c in st.session_state.customers if c.get('status') == filter_status]
    
    if filtered_customers:
        for customer in filtered_customers:
            # Create columns for better layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {customer['id']}")
                st.write(f"**Name:** {customer['name']}")
                st.write(f"**Email:** {customer['email']}")
                if customer.get('phone'):
                    st.write(f"**Phone:** {customer['phone']}")
                if customer.get('country'):
                    st.write(f"**Country:** {customer['country']}")
                if customer.get('goal'):
                    st.write(f"**Goal:** {customer['goal']}")
                
            with col2:
                if customer.get('budget'):
                    st.write(f"**Budget:** {customer['budget']}")
                if customer.get('webinar_join'):
                    st.write(f"**Webinar Join:** {customer['webinar_join']}")
                if customer.get('webinar_leave'):
                    st.write(f"**Webinar Leave:** {customer['webinar_leave']}")
                st.write(f"**Asked Questions:** {'Yes' if customer.get('asked_q') else 'No'}")
                st.write(f"**Referred:** {'Yes' if customer.get('referred') else 'No'}")
                st.write(f"**Past Touchpoints:** {customer.get('past_touchpoints', 0)}")
            
            # Qualification info in a separate section with highlight
            if customer.get('status'):
                status_color = "green" if customer.get('status') == "Qualified" else "orange"
                st.markdown(f"**Status:** <span style='color:{status_color}'>{customer.get('status')}</span>", unsafe_allow_html=True)
                if customer.get('score'):
                    st.write(f"**Score:** {customer.get('score')}")
                if customer.get('reasoning'):
                    with st.expander("Qualification Reasoning"):
                        st.write(customer.get('reasoning'))
            
            st.write("---")
    else:
        st.info("No customers found.")

elif page == "Add Customer":
    st.header("Add New Customer")
    with st.form("add_customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone (optional)")
            country = st.text_input("Country (optional)")
            goal = st.text_input("Goal (optional)")
        
        with col2:
            budget = st.selectbox("Budget (optional)", ["", "Self", "Company"])
            webinar_date = st.date_input("Webinar Date (optional)", value=None)
            join_time = st.time_input("Webinar Join Time (optional)", value=None)
            leave_time = st.time_input("Webinar Leave Time (optional)", value=None)
        
        col3, col4 = st.columns(2)
        with col3:
            asked_q = st.checkbox("Asked Questions During Webinar")
            referred = st.checkbox("Customer Was Referred")
        
        with col4:
            past_touchpoints = st.number_input("Past Touchpoints", min_value=0, value=0)
        
        submitted = st.form_submit_button("Add Customer")
        if submitted:
            if name and email:
                # Convert date and time inputs to datetime objects
                webinar_join_dt = None
                webinar_leave_dt = None
                
                if webinar_date and join_time:
                    webinar_join_dt = datetime.combine(webinar_date, join_time)
                    
                    if leave_time:
                        webinar_leave_dt = datetime.combine(webinar_date, leave_time)
                        # If leave time is earlier than join time, assume it's the next day
                        if webinar_leave_dt < webinar_join_dt:
                            webinar_leave_dt = datetime.combine(webinar_date + datetime.timedelta(days=1), leave_time)
                
                create_customer(
                    name, email, phone, country, goal, budget,
                    webinar_join_dt, webinar_leave_dt, asked_q, referred, past_touchpoints
                )
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
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Name", value=selected_customer['name'])
                    email = st.text_input("Email", value=selected_customer['email'])
                    phone = st.text_input("Phone", value=selected_customer.get('phone', ''))
                    country = st.text_input("Country", value=selected_customer.get('country', ''))
                    goal = st.text_input("Goal", value=selected_customer.get('goal', ''))
                
                with col2:
                    budget = st.selectbox("Budget", 
                                        ["", "Self", "Company"], 
                                        index=["", "Self", "Company"].index(selected_customer.get('budget', '')) if selected_customer.get('budget') in ["Self", "Company"] else 0)
                    
                    # Handle webinar date and time fields
                    webinar_date = None
                    join_time = None
                    leave_time = None
                    
                    if selected_customer.get('webinar_join'):
                        try:
                            webinar_join_dt = datetime.fromisoformat(selected_customer.get('webinar_join'))
                            webinar_date = webinar_join_dt.date()
                            join_time = webinar_join_dt.time()
                        except (ValueError, TypeError):
                            pass
                            
                    if selected_customer.get('webinar_leave'):
                        try:
                            webinar_leave_dt = datetime.fromisoformat(selected_customer.get('webinar_leave'))
                            leave_time = webinar_leave_dt.time()
                        except (ValueError, TypeError):
                            pass
                    
                    webinar_date = st.date_input("Webinar Date", value=webinar_date)
                    join_time = st.time_input("Webinar Join Time", value=join_time)
                    leave_time = st.time_input("Webinar Leave Time", value=leave_time)
                
                col3, col4 = st.columns(2)
                with col3:
                    asked_q = st.checkbox("Asked Questions During Webinar", value=selected_customer.get('asked_q', False))
                    referred = st.checkbox("Customer Was Referred", value=selected_customer.get('referred', False))
                
                with col4:
                    past_touchpoints = st.number_input("Past Touchpoints", 
                                                    min_value=0, 
                                                    value=selected_customer.get('past_touchpoints', 0))
                
                submitted = st.form_submit_button("Update Customer")
                if submitted:
                    if name and email:
                        # Convert date and time inputs to datetime objects
                        webinar_join_dt = None
                        webinar_leave_dt = None
                        
                        if webinar_date and join_time:
                            webinar_join_dt = datetime.combine(webinar_date, join_time)
                            
                            if leave_time:
                                webinar_leave_dt = datetime.combine(webinar_date, leave_time)
                                # If leave time is earlier than join time, assume it's the next day
                                if webinar_leave_dt < webinar_join_dt:
                                    webinar_leave_dt = datetime.combine(webinar_date + datetime.timedelta(days=1), leave_time)
                        
                        update_customer(
                            customer_id, name, email, phone, country, goal, budget,
                            webinar_join_dt, webinar_leave_dt, asked_q, referred, past_touchpoints
                        )
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

elif page == "Qualify Customer":
    st.header("Qualify Customer")
    if st.session_state.customers:
        # Filter out already qualified customers
        unqualified_customers = [c for c in st.session_state.customers if not c.get('status')]
        
        if unqualified_customers:
            customer_id = st.selectbox(
                "Select Customer to Qualify",
                options=[c['id'] for c in unqualified_customers],
                format_func=lambda id: next((f"{c['id']} - {c['name']}" for c in unqualified_customers if c['id'] == id), str(id))
            )
            
            if st.button("Qualify Customer"):
                qualify_customer(customer_id)
        else:
            st.info("All customers have already been qualified.")
    else:
        st.info("No customers available to qualify.")