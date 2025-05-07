import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Callable, Optional

def display_customer_list(
    customers: List[Dict[str, Any]], 
    on_edit: Optional[Callable[[int], None]] = None,
    on_delete: Optional[Callable[[int], None]] = None,
    show_actions: bool = True
):
    """Display a list of customers as a dataframe with optional actions."""
    if not customers:
        st.info("No customers found.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(customers)
    
    # Reorder and select columns for display
    display_columns = [
        'id', 'name', 'email', 'title', 'goal', 'budget', 'country',
        'score', 'status', 'reasoning', 'engaged_mins', 'asked_question'
    ]
    
    # Ensure all columns exist
    display_columns = [col for col in display_columns if col in df.columns]
    
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
    if 'Asked Questions' in df_display.columns:
        df_display['Asked Questions'] = df_display['Asked Questions'].map({True: 'Yes', False: 'No'})
    
    # Format score and status
    if 'Qualification Score' in df_display.columns:
        df_display['Qualification Score'] = df_display['Qualification Score'].fillna('Not Qualified')
    if 'Status' in df_display.columns:
        df_display['Status'] = df_display['Status'].fillna('Not Qualified')
    
    # Configure column formatting
    column_config = {
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
    
    # Add actions column if callbacks are provided
    if show_actions and (on_edit or on_delete):
        # Add a dummy column for actions that will be populated with buttons
        df_display['Actions'] = 'Actions'
        
        # Show the dataframe
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        
        # Add action buttons below the dataframe
        col1, col2 = st.columns(2)
        with col1:
            if on_edit:
                customer_id = st.selectbox("Select customer to edit:", 
                                         df['id'].tolist(), 
                                         format_func=lambda x: df[df['id']==x]['name'].iloc[0])
                if st.button("Edit Selected"):
                    on_edit(customer_id)
        
        with col2:
            if on_delete:
                customer_id = st.selectbox("Select customer to delete:", 
                                          df['id'].tolist(), 
                                          format_func=lambda x: df[df['id']==x]['name'].iloc[0],
                                          key="delete_select")
                if st.button("Delete Selected", type="primary"):
                    on_delete(customer_id)
    else:
        # Show the dataframe without actions
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
    
    # Display summary statistics
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_customers = len(df_display)
        qualified_customers = len(df_display[df_display['Status'] == 'SQL']) if 'Status' in df_display else 0
        st.metric("Total Customers", total_customers)
        st.metric("Qualified Customers", qualified_customers)
    
    with col2:
        if 'Qualification Score' in df_display:
            avg_score = df_display['Qualification Score'].replace('Not Qualified', 0).mean()
            st.metric("Average Score", f"{avg_score:.1f}")
        if 'Engagement (mins)' in df_display:
            avg_engagement = df_display['Engagement (mins)'].fillna(0).mean()
            st.metric("Average Engagement", f"{avg_engagement:.1f} mins")
    
    with col3:
        if 'Asked Questions' in df_display:
            questions_asked = len(df_display[df_display['Asked Questions'] == 'Yes'])
            st.metric("Customers with Questions", questions_asked)
        if qualified_customers > 0 and total_customers > 0:
            st.metric("Qualification Rate", f"{(qualified_customers/total_customers*100):.1f}%") 