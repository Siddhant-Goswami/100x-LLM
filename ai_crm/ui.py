import streamlit as st
import requests
from typing import List, Optional
from datetime import datetime, date, time
import pandas as pd

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

def create_customer(customer_data: dict):
    """Create a new customer"""
    try:
        response = requests.post(f"{BASE_URL}/customers", json=customer_data)
        if response.status_code == 200:
            st.success("Customer created successfully!")
            fetch_customers()
        else:
            st.error(f"Error creating customer: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating customer: {str(e)}")

def update_customer(customer_id: int, customer_data: dict):
    """Update an existing customer"""
    try:
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
st.title("AI-Powered Customer Management System")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose an operation", ["View Customers", "Add Customer", "Update Customer", "Delete Customer"])

# Fetch customers on initial load
fetch_customers()

def display_customer(customer):
    """Helper function to display customer information"""
    st.write(f"**ID:** {customer['id']}")
    st.write(f"**Name:** {customer['name']}")
    st.write(f"**Email:** {customer['email']}")
    st.write(f"**Title:** {customer['title']}")
    st.write(f"**Goal:** {customer['goal']}")
    st.write(f"**Budget:** {customer['budget']}")
    st.write(f"**Country:** {customer['country']}")
    
    if customer.get('phone'):
        st.write(f"**Phone:** {customer['phone']}")
    if customer.get('address'):
        st.write(f"**Address:** {customer['address']}")
    
    # Qualification information
    st.write("**Qualification Status:**")
    st.write(f"- Score: {customer.get('score', 'Not qualified')}")
    st.write(f"- Status: {customer.get('status', 'Not qualified')}")
    if customer.get('reasoning'):
        st.write(f"- Reasoning: {customer['reasoning']}")
    
    # Engagement information
    if customer.get('engaged_mins'):
        st.write(f"**Engagement:** {customer['engaged_mins']} minutes")
    if customer.get('asked_question'):
        st.write("**Asked Questions:** Yes")
    
    st.write("---")

if page == "View Customers":
    st.header("All Customers")
    
    # Add filter for qualified customers
    show_qualified = st.checkbox("Show only qualified customers")
    
    if st.session_state.customers:
        filtered_customers = [c for c in st.session_state.customers if not show_qualified or c.get('score', 0) >= 70]
        
        if filtered_customers:
            # Convert to DataFrame for better display
            df = pd.DataFrame(filtered_customers)
            
            # Reorder and select columns for display
            display_columns = [
                'id', 'name', 'email', 'title', 'goal', 'budget', 'country',
                'score', 'status', 'reasoning', 'engaged_mins', 'asked_question'
            ]
            
            # Rename columns for better display
            column_names = {
                'id': 'ID',
                'name': 'Name',
                'email': 'Email',
                'title': 'Title',
                'goal': 'Goal',
                'budget': 'Budget',
                'country': 'Country',
                'score': 'Qualification Score',
                'status': 'Status',
                'reasoning': 'Qualification Reasoning',
                'engaged_mins': 'Engagement (mins)',
                'asked_question': 'Asked Questions'
            }
            
            # Select and rename columns
            df_display = df[display_columns].rename(columns=column_names)
            
            # Format boolean values
            df_display['Asked Questions'] = df_display['Asked Questions'].map({True: 'Yes', False: 'No'})
            
            # Format score and status
            df_display['Qualification Score'] = df_display['Qualification Score'].fillna('Not Qualified')
            df_display['Status'] = df_display['Status'].fillna('Not Qualified')
            
            # Display the dataframe with styling
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width=50),
                    "Name": st.column_config.TextColumn("Name", width=150),
                    "Email": st.column_config.TextColumn("Email", width=200),
                    "Title": st.column_config.TextColumn("Title", width=150),
                    "Goal": st.column_config.TextColumn("Goal", width=200),
                    "Budget": st.column_config.TextColumn("Budget", width=100),
                    "Country": st.column_config.TextColumn("Country", width=100),
                    "Qualification Score": st.column_config.NumberColumn("Score", width=100),
                    "Status": st.column_config.TextColumn("Status", width=100),
                    "Qualification Reasoning": st.column_config.TextColumn("Reasoning", width=200),
                    "Engagement (mins)": st.column_config.NumberColumn("Engagement", width=100),
                    "Asked Questions": st.column_config.TextColumn("Questions", width=100)
                }
            )
            
            # Add summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_customers = len(df_display)
                qualified_customers = len(df_display[df_display['Status'] == 'SQL'])
                st.metric("Total Customers", total_customers)
                st.metric("Qualified Customers", qualified_customers)
            
            with col2:
                avg_score = df_display['Qualification Score'].replace('Not Qualified', 0).mean()
                avg_engagement = df_display['Engagement (mins)'].mean()
                st.metric("Average Score", f"{avg_score:.1f}")
                st.metric("Average Engagement", f"{avg_engagement:.1f} mins")
            
            with col3:
                questions_asked = len(df_display[df_display['Asked Questions'] == 'Yes'])
                st.metric("Customers with Questions", questions_asked)
                st.metric("Qualification Rate", f"{(qualified_customers/total_customers*100):.1f}%")
            
        else:
            st.info("No customers match the current filter.")
    else:
        st.info("No customers found.")

elif page == "Add Customer":
    st.header("Add New Customer")
    with st.form("add_customer_form"):
        # Required fields
        name = st.text_input("Name *")
        email = st.text_input("Email *")
        title = st.text_input("Title *")
        goal = st.text_area("Goal *")
        budget = st.selectbox("Budget *", ["company", "self"])
        country = st.text_input("Country *")
        
        # Optional fields
        phone = st.text_input("Phone (optional)")
        address = st.text_area("Address (optional)")
        asked_question = st.checkbox("Asked Questions")
        
        # Webinar information
        st.subheader("Webinar Information (Optional)")
        col1, col2 = st.columns(2)
        with col1:
            webinar_date = st.date_input("Webinar Date")
            webinar_time = st.time_input("Webinar Time")
        with col2:
            webinar_leave_date = st.date_input("Webinar Leave Date")
            webinar_leave_time = st.time_input("Webinar Leave Time")
        
        submitted = st.form_submit_button("Add Customer")
        if submitted:
            if name and email and title and goal and budget and country:
                customer_data = {
                    "name": name,
                    "email": email,
                    "title": title,
                    "goal": goal,
                    "budget": budget,
                    "country": country,
                    "phone": phone if phone else None,
                    "address": address if address else None,
                    "asked_question": asked_question
                }
                
                # Combine date and time for webinar timestamps
                if webinar_date and webinar_time and webinar_leave_date and webinar_leave_time:
                    webinar_join = datetime.combine(webinar_date, webinar_time)
                    webinar_leave = datetime.combine(webinar_leave_date, webinar_leave_time)
                    customer_data["webinar_join"] = webinar_join.isoformat()
                    customer_data["webinar_leave"] = webinar_leave.isoformat()
                
                create_customer(customer_data)
            else:
                st.warning("Please fill in all required fields (marked with *)")

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
                # Required fields
                name = st.text_input("Name *", value=selected_customer['name'])
                email = st.text_input("Email *", value=selected_customer['email'])
                title = st.text_input("Title *", value=selected_customer['title'])
                goal = st.text_area("Goal *", value=selected_customer['goal'])
                budget = st.selectbox("Budget *", ["company", "self"], index=0 if selected_customer['budget'] == "company" else 1)
                country = st.text_input("Country *", value=selected_customer['country'])
                
                # Optional fields
                phone = st.text_input("Phone", value=selected_customer.get('phone', ''))
                address = st.text_area("Address", value=selected_customer.get('address', ''))
                asked_question = st.checkbox("Asked Questions", value=selected_customer.get('asked_question', False))
                
                # Webinar information
                st.subheader("Webinar Information")
                col1, col2 = st.columns(2)
                
                # Parse existing webinar times if they exist
                webinar_join = None
                webinar_leave = None
                if selected_customer.get('webinar_join'):
                    webinar_join = datetime.fromisoformat(selected_customer['webinar_join'])
                if selected_customer.get('webinar_leave'):
                    webinar_leave = datetime.fromisoformat(selected_customer['webinar_leave'])
                
                with col1:
                    webinar_date = st.date_input(
                        "Webinar Date",
                        value=webinar_join.date() if webinar_join else date.today()
                    )
                    webinar_time = st.time_input(
                        "Webinar Time",
                        value=webinar_join.time() if webinar_join else time(0, 0)
                    )
                with col2:
                    webinar_leave_date = st.date_input(
                        "Webinar Leave Date",
                        value=webinar_leave.date() if webinar_leave else date.today()
                    )
                    webinar_leave_time = st.time_input(
                        "Webinar Leave Time",
                        value=webinar_leave.time() if webinar_leave else time(0, 0)
                    )
                
                submitted = st.form_submit_button("Update Customer")
                if submitted:
                    if name and email and title and goal and budget and country:
                        customer_data = {
                            "name": name,
                            "email": email,
                            "title": title,
                            "goal": goal,
                            "budget": budget,
                            "country": country,
                            "phone": phone if phone else None,
                            "address": address if address else None,
                            "asked_question": asked_question
                        }
                        
                        # Combine date and time for webinar timestamps
                        webinar_join = datetime.combine(webinar_date, webinar_time)
                        webinar_leave = datetime.combine(webinar_leave_date, webinar_leave_time)
                        customer_data["webinar_join"] = webinar_join.isoformat()
                        customer_data["webinar_leave"] = webinar_leave.isoformat()
                        
                        update_customer(customer_id, customer_data)
                    else:
                        st.warning("Please fill in all required fields (marked with *)")
    else:
        st.info("No customers available to update.")

elif page == "Delete Customer":
    st.header("Delete Customer")
    if st.session_state.customers:
        customer_id = st.selectbox(
            "Select Customer to Delete",
            options=[c['id'] for c in st.session_state.customers]
        )
        
        # Show customer details before deletion
        selected_customer = next((c for c in st.session_state.customers if c['id'] == customer_id), None)
        if selected_customer:
            st.warning("You are about to delete the following customer:")
            display_customer(selected_customer)
            
            if st.button("Confirm Delete"):
                delete_customer(customer_id)
    else:
        st.info("No customers available to delete.")