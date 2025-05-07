import streamlit as st
import asyncio
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import components
from frontend.api import ApiClient
from frontend.components.customer_list import display_customer_list
from frontend.components.customer_form import customer_form

# Set page config
st.set_page_config(
    page_title="AI-CRM Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "customers" not in st.session_state:
    st.session_state.customers = []
if "current_customer" not in st.session_state:
    st.session_state.current_customer = None
if "show_edit_form" not in st.session_state:
    st.session_state.show_edit_form = False

# Custom async function to load data
async def load_data():
    try:
        st.session_state.customers = await ApiClient.get_customers()
        logger.info(f"Loaded {len(st.session_state.customers)} customers")
    except Exception as e:
        st.error(f"Error loading customers: {str(e)}")
        logger.error(f"Error loading customers: {str(e)}", exc_info=True)

# Callbacks for customer actions
async def create_customer(customer_data: Dict[str, Any]):
    try:
        new_customer = await ApiClient.create_customer(customer_data)
        st.success(f"Customer {new_customer['name']} created successfully!")
        st.session_state.customers.append(new_customer)
    except Exception as e:
        st.error(f"Error creating customer: {str(e)}")
        logger.error(f"Error creating customer: {str(e)}", exc_info=True)

async def update_customer(customer_data: Dict[str, Any]):
    try:
        updated_customer = await ApiClient.update_customer(customer_data["id"], customer_data)
        st.success(f"Customer {updated_customer['name']} updated successfully!")
        # Update the customer in the session state
        for i, customer in enumerate(st.session_state.customers):
            if customer["id"] == updated_customer["id"]:
                st.session_state.customers[i] = updated_customer
                break
        st.session_state.show_edit_form = False
        st.session_state.current_customer = None
    except Exception as e:
        st.error(f"Error updating customer: {str(e)}")
        logger.error(f"Error updating customer: {str(e)}", exc_info=True)

async def delete_customer(customer_id: int):
    try:
        deleted_customer = await ApiClient.delete_customer(customer_id)
        st.success(f"Customer {deleted_customer['name']} deleted successfully!")
        # Remove the customer from the session state
        st.session_state.customers = [c for c in st.session_state.customers if c["id"] != customer_id]
    except Exception as e:
        st.error(f"Error deleting customer: {str(e)}")
        logger.error(f"Error deleting customer: {str(e)}", exc_info=True)

def edit_customer(customer_id: int):
    # Find the customer in the session state
    customer = next((c for c in st.session_state.customers if c["id"] == customer_id), None)
    if customer:
        st.session_state.current_customer = customer
        st.session_state.show_edit_form = True
        st.experimental_rerun()

# Main app
st.title("🤖 AI-CRM Dashboard")

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Dashboard", "Add Customer"])

# Load data on first load
if len(st.session_state.customers) == 0:
    asyncio.run(load_data())

# Refresh button
if st.sidebar.button("Refresh Data"):
    asyncio.run(load_data())

# Display current page
if page == "Dashboard":
    st.header("Customer Dashboard")
    
    # Filter options
    show_qualified = st.checkbox("Show only qualified leads", value=False)
    
    # Filter customers based on selection
    filtered_customers = st.session_state.customers
    if show_qualified:
        filtered_customers = [c for c in filtered_customers if c.get('score', 0) >= 70]
    
    # Show edit form if needed
    if st.session_state.show_edit_form and st.session_state.current_customer:
        customer_form(
            lambda data: asyncio.run(update_customer(data)),
            title=f"Edit Customer: {st.session_state.current_customer['name']}",
            submit_label="Update Customer",
            initial_values=st.session_state.current_customer
        )
        if st.button("Cancel Edit"):
            st.session_state.show_edit_form = False
            st.session_state.current_customer = None
            st.experimental_rerun()
    else:
        # Display customer list with actions
        display_customer_list(
            filtered_customers,
            on_edit=edit_customer,
            on_delete=lambda id: asyncio.run(delete_customer(id))
        )

elif page == "Add Customer":
    st.header("Add New Customer")
    customer_form(
        lambda data: asyncio.run(create_customer(data)),
        title="Add New Customer",
        submit_label="Create Customer"
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.info("AI-CRM - Qualifying leads with AI")
st.sidebar.text("Version 1.0.0") 