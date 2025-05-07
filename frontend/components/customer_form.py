import streamlit as st
from datetime import datetime, date, time
from typing import Dict, Any, Optional, Callable

def customer_form(
    on_submit: Callable[[Dict[str, Any]], None],
    title: str = "Add Customer",
    submit_label: str = "Submit",
    initial_values: Optional[Dict[str, Any]] = None
):
    """Display a form for creating or updating a customer."""
    initial_values = initial_values or {}
    
    with st.form(f"{title.lower().replace(' ', '_')}_form"):
        st.subheader(title)
        
        # Required fields
        name = st.text_input("Name *", value=initial_values.get("name", ""))
        email = st.text_input("Email *", value=initial_values.get("email", ""))
        title_field = st.text_input("Title/Role *", value=initial_values.get("title", ""))
        goal = st.text_area("Goal *", value=initial_values.get("goal", ""))
        budget = st.selectbox(
            "Budget *", 
            ["company", "self"], 
            index=0 if initial_values.get("budget") != "self" else 1
        )
        country = st.text_input("Country *", value=initial_values.get("country", ""))
        
        # Optional fields
        st.markdown("---")
        st.markdown("**Additional Information (Optional)**")
        
        phone = st.text_input("Phone", value=initial_values.get("phone", ""))
        address = st.text_input("Address", value=initial_values.get("address", ""))
        
        # Webinar information
        st.markdown("**Webinar Information (if applicable)**")
        
        # Handle webinar dates
        webinar_date = None
        webinar_join_time = None
        webinar_leave_time = None
        
        if initial_values.get("webinar_join"):
            dt = datetime.fromisoformat(initial_values["webinar_join"])
            webinar_date = dt.date()
            webinar_join_time = dt.time()
        
        if initial_values.get("webinar_leave"):
            dt = datetime.fromisoformat(initial_values["webinar_leave"])
            webinar_leave_time = dt.time()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            webinar_date = st.date_input("Webinar Date", value=webinar_date)
        with col2:
            webinar_join_time = st.time_input("Join Time", value=webinar_join_time or time(9, 0))
        with col3:
            webinar_leave_time = st.time_input("Leave Time", value=webinar_leave_time or time(10, 0))
        
        # Activity information
        asked_question = st.checkbox(
            "Asked Questions During Webinar", 
            value=initial_values.get("asked_question", False)
        )
        
        # Submit button
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            # Validate required fields
            if not name or not email or not title_field or not goal or not country:
                st.error("Please fill in all required fields.")
                return
            
            # Create webinar datetimes if date is provided
            webinar_join = None
            webinar_leave = None
            if webinar_date:
                webinar_join = datetime.combine(webinar_date, webinar_join_time)
                webinar_leave = datetime.combine(webinar_date, webinar_leave_time)
            
            # Build customer data
            customer_data = {
                "name": name,
                "email": email,
                "title": title_field,
                "goal": goal,
                "budget": budget,
                "country": country,
                "phone": phone or None,
                "address": address or None,
                "webinar_join": webinar_join.isoformat() if webinar_join else None,
                "webinar_leave": webinar_leave.isoformat() if webinar_leave else None,
                "asked_question": asked_question
            }
            
            # Add ID if updating an existing customer
            if "id" in initial_values:
                customer_data["id"] = initial_values["id"]
            
            # Call the callback with the customer data
            on_submit(customer_data) 