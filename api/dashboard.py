# -*- coding: utf-8 -*-
# Insurance Company Support Team Dashboard
# 
# This dashboard provides real-time insights into support team performance,
# ticket management, and customer satisfaction metrics.

from datetime import datetime, timedelta
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import random

# Set random seed for consistent mock data
np.random.seed(42)
random.seed(42)

# Generate mock insurance support data
def generate_support_data():
    """Generate realistic mock data for insurance support team dashboard"""
    
    # Date range for the last 365 days
    start_date = datetime.now() - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=datetime.now(), freq='D')
    
    # Generate daily ticket data
    data = []
    for date in dates:
        # Simulate seasonal patterns and weekday effects
        weekday = date.weekday()
        is_weekend = weekday >= 5
        
        # Base ticket counts
        base_tickets = 80 if is_weekend else 120
        
        # Add some randomness
        total_tickets = max(1, int(np.random.normal(base_tickets, base_tickets * 0.2)))
        
        # Ticket categories with realistic distribution
        categories = ['Claims', 'Policy Questions', 'Billing', 'Technical Support', 'Complaints']
        category_dist = [0.35, 0.25, 0.20, 0.15, 0.05]
        
        # Priority levels
        priorities = ['Low', 'Medium', 'High', 'Critical']
        priority_dist = [0.40, 0.35, 0.20, 0.05]
        
        # Status distribution
        statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
        status_dist = [0.15, 0.25, 0.45, 0.15]
        
        # Generate tickets for this day
        for _ in range(total_tickets):
            category = np.random.choice(categories, p=category_dist)
            priority = np.random.choice(priorities, p=priority_dist)
            status = np.random.choice(statuses, p=status_dist)
            
            # Resolution time based on priority and category
            base_resolution_hours = {
                'Low': 24, 'Medium': 8, 'High': 4, 'Critical': 2
            }
            category_multiplier = {
                'Claims': 2.0, 'Policy Questions': 1.0, 'Billing': 1.5, 
                'Technical Support': 2.5, 'Complaints': 3.0
            }
            
            resolution_hours = base_resolution_hours[priority] * category_multiplier[category]
            resolution_hours = max(0.5, np.random.normal(resolution_hours, resolution_hours * 0.3))
            
            # Customer satisfaction (1-5 scale)
            satisfaction = np.random.normal(4.2, 0.8)
            satisfaction = max(1, min(5, satisfaction))
            
            data.append({
                'date': date,
                'category': category,
                'priority': priority,
                'status': status,
                'resolution_hours': resolution_hours,
                'satisfaction': satisfaction,
                'ticket_id': f"TK{random.randint(10000, 99999)}"
            })
    
    return pd.DataFrame(data)

# Generate the data
support_df = generate_support_data()

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Insurance Support Dashboard",
    page_icon="🛡️",
    # Make the content take up the width of the page:
    layout="wide",
)


"""
# Insurance Support Team Dashboard 🛡️

Real-time insights into support team performance, ticket management, and customer satisfaction metrics.
"""

""  # Add a little vertical space. Same as st.write("").
""

"""
## Current Month Summary
"""

""

# Get current month data
current_month = datetime.now().month
current_year = datetime.now().year
last_month = current_month - 1 if current_month > 1 else 12
last_month_year = current_year if current_month > 1 else current_year - 1

df_current = support_df[
    (support_df["date"].dt.month == current_month) & 
    (support_df["date"].dt.year == current_year)
]
df_last_month = support_df[
    (support_df["date"].dt.month == last_month) & 
    (support_df["date"].dt.year == last_month_year)
]

# Calculate KPIs
total_tickets_current = len(df_current)
total_tickets_last = len(df_last_month)

avg_resolution_current = df_current["resolution_hours"].mean()
avg_resolution_last = df_last_month["resolution_hours"].mean()

avg_satisfaction_current = df_current["satisfaction"].mean()
avg_satisfaction_last = df_last_month["satisfaction"].mean()

open_tickets_current = len(df_current[df_current["status"].isin(["Open", "In Progress"])])
open_tickets_last = len(df_last_month[df_last_month["status"].isin(["Open", "In Progress"])])

resolved_tickets_current = len(df_current[df_current["status"].isin(["Resolved", "Closed"])])
resolved_tickets_last = len(df_last_month[df_last_month["status"].isin(["Resolved", "Closed"])])

critical_tickets_current = len(df_current[df_current["priority"] == "Critical"])
critical_tickets_last = len(df_last_month[df_last_month["priority"] == "Critical"])

claims_tickets_current = len(df_current[df_current["category"] == "Claims"])
claims_tickets_last = len(df_last_month[df_last_month["category"] == "Claims"])


with st.container(horizontal=True, gap="medium"):
    cols = st.columns(3, gap="medium")

    with cols[0]:
        st.metric(
            "Total Tickets",
            f"{total_tickets_current:,}",
            delta=f"{total_tickets_current - total_tickets_last:,}",
            delta_color="inverse",
            help="Total support tickets received this month"
        )

    with cols[1]:
        st.metric(
            "Avg Resolution Time",
            f"{avg_resolution_current:.1f}h",
            delta=f"{avg_resolution_current - avg_resolution_last:.1f}h",
            delta_color="inverse",
            help="Average time to resolve tickets in hours"
        )

    with cols[2]:
        st.metric(
            "Customer Satisfaction",
            f"{avg_satisfaction_current:.2f}/5.0",
            delta=f"{avg_satisfaction_current - avg_satisfaction_last:.2f}",
            help="Average customer satisfaction rating"
        )

    cols = st.columns(3, gap="medium")

    with cols[0]:
        st.metric(
            "Open Tickets",
            f"{open_tickets_current:,}",
            delta=f"{open_tickets_current - open_tickets_last:,}",
            delta_color="inverse",
            help="Tickets currently open or in progress"
        )

    with cols[1]:
        st.metric(
            "Resolved Tickets",
            f"{resolved_tickets_current:,}",
            delta=f"{resolved_tickets_current - resolved_tickets_last:,}",
            help="Tickets resolved or closed this month"
        )

    with cols[2]:
        st.metric(
            "Critical Tickets",
            f"{critical_tickets_current:,}",
            delta=f"{critical_tickets_current - critical_tickets_last:,}",
            delta_color="inverse",
            help="High priority critical tickets"
        )

    cols = st.columns(2, gap="medium")

    with cols[0]:
        # Most common ticket category
        most_common_category = df_current["category"].value_counts().head(1).index[0]
        category_icons = {
            "Claims": "📋",
            "Policy Questions": "📄",
            "Billing": "💳",
            "Technical Support": "🔧",
            "Complaints": "⚠️"
        }
        st.metric(
            "Most Common Issue",
            f"{category_icons[most_common_category]} {most_common_category}",
            help="Most frequently reported issue type"
        )

    with cols[1]:
        # Resolution rate
        resolution_rate = (resolved_tickets_current / total_tickets_current * 100) if total_tickets_current > 0 else 0
        last_resolution_rate = (resolved_tickets_last / total_tickets_last * 100) if total_tickets_last > 0 else 0
        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%",
            delta=f"{resolution_rate - last_resolution_rate:.1f}%",
            help="Percentage of tickets resolved this month"
        )

""
""

"""
## Support Performance Analytics
"""

# Time period selection
YEARS = sorted(support_df["date"].dt.year.unique())
selected_years = st.pills(
    "Select years to compare", YEARS, default=YEARS[-2:], selection_mode="multi"
)

if not selected_years:
    st.warning("You must select at least 1 year.", icon=":material/warning:")

df = support_df[support_df["date"].dt.year.isin(selected_years)]

cols = st.columns([3, 1])

with cols[0].container(border=True, height="stretch"):
    "### Daily Ticket Volume"

    # Create daily ticket counts
    daily_tickets = df.groupby(['date', df['date'].dt.year]).size().reset_index(name='ticket_count')
    
    st.altair_chart(
        alt.Chart(daily_tickets)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            alt.X("date:T").title("Date"),
            alt.Y("ticket_count:Q").title("Daily Tickets"),
            alt.Color("year(date):N").title("Year"),
            alt.Tooltip(['date:T', 'ticket_count:Q'])
        )
        .configure_legend(orient="bottom")
    )

with cols[1].container(border=True, height="stretch"):
    "### Ticket Categories"

    # Category distribution
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    
    st.altair_chart(
        alt.Chart(category_counts)
        .mark_arc(innerRadius=20)
        .encode(
            alt.Theta("count:Q").title("Count"),
            alt.Color("category:N").title("Category"),
            alt.Tooltip(['category:N', 'count:Q'])
        )
        .configure_legend(orient="bottom")
    )


cols = st.columns(2)

with cols[0].container(border=True, height="stretch"):
    "### Resolution Time Trends"

    # Calculate 14-day rolling average resolution time
    daily_resolution = df.groupby('date')['resolution_hours'].mean().reset_index()
    daily_resolution['rolling_avg'] = daily_resolution['resolution_hours'].rolling(window=14, min_periods=1).mean()
    
    st.altair_chart(
        alt.Chart(daily_resolution)
        .mark_line(size=2)
        .encode(
            alt.X("date:T").title("Date"),
            alt.Y("rolling_avg:Q").title("Avg Resolution Time (hours)"),
            alt.Tooltip(['date:T', 'rolling_avg:Q'])
        )
    )

with cols[1].container(border=True, height="stretch"):
    "### Monthly Ticket Volume"

    # Monthly ticket counts
    monthly_tickets = df.groupby([df['date'].dt.year, df['date'].dt.month]).size().reset_index(name='ticket_count')
    monthly_tickets['month_year'] = monthly_tickets['year'].astype(str) + '-' + monthly_tickets['month'].astype(str).str.zfill(2)
    
    st.altair_chart(
        alt.Chart(monthly_tickets)
        .mark_bar()
        .encode(
            alt.X("month_year:N").title("Month"),
            alt.Y("ticket_count:Q").title("Monthly Tickets"),
            alt.Color("year:N").title("Year"),
            alt.Tooltip(['month_year:N', 'ticket_count:Q'])
        )
        .configure_legend(orient="bottom")
    )

cols = st.columns(2)

with cols[0].container(border=True, height="stretch"):
    "### Priority Distribution by Month"
    ""

    # Monthly priority breakdown
    monthly_priority = df.groupby([df['date'].dt.month, 'priority']).size().reset_index(name='count')
    monthly_priority['month'] = monthly_priority['date']
    
    st.altair_chart(
        alt.Chart(monthly_priority)
        .mark_bar()
        .encode(
            alt.X("month:O", title="Month"),
            alt.Y("count:Q", title="Tickets").stack("normalize"),
            alt.Color("priority:N").title("Priority"),
            alt.Tooltip(['month:O', 'priority:N', 'count:Q'])
        )
        .configure_legend(orient="bottom")
    )

with cols[1].container(border=True, height="stretch"):
    "### Customer Satisfaction Trends"

    # Calculate monthly satisfaction averages
    monthly_satisfaction = df.groupby([df['date'].dt.year, df['date'].dt.month])['satisfaction'].mean().reset_index()
    monthly_satisfaction['month_year'] = monthly_satisfaction['year'].astype(str) + '-' + monthly_satisfaction['month'].astype(str).str.zfill(2)
    
    st.altair_chart(
        alt.Chart(monthly_satisfaction)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            alt.X("month_year:N").title("Month"),
            alt.Y("satisfaction:Q").title("Avg Satisfaction (1-5)").scale(zero=False),
            alt.Color("year:N").title("Year"),
            alt.Tooltip(['month_year:N', 'satisfaction:Q'])
        )
        .configure_legend(orient="bottom")
    )

"""
## Recent Support Tickets
"""

# Show recent tickets
recent_tickets = df.nlargest(100, 'date')[['date', 'ticket_id', 'category', 'priority', 'status', 'resolution_hours', 'satisfaction']].sort_values('date', ascending=False)

st.dataframe(
    recent_tickets,
    use_container_width=True,
    hide_index=True
)