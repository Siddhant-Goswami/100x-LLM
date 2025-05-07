import csv
import os
import threading
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from ai_crm.models import Customer, CustomerStatus

# Thread lock for CSV file access
_LOCK = threading.Lock()

# Get the directory where this file is located
CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
CSV_FILE = CURRENT_DIR / "customers.csv"

def init_db() -> None:
    """Initialize the CSV database if it doesn't exist."""
    CSV_FILE.parent.mkdir(exist_ok=True)
    if not CSV_FILE.exists():
        with _LOCK, open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'name', 'email', 'phone', 'address', 'title', 'goal',
                'budget', 'country', 'webinar_join', 'webinar_leave',
                'engaged_mins', 'asked_question', 'score', 'reasoning',
                'status', 'created_at', 'updated_at'
            ])

def _customer_to_row(customer: Customer) -> List:
    """Convert a Customer object to a CSV row."""
    return [
        customer.id,
        customer.name,
        customer.email,
        customer.phone,
        customer.address,
        customer.title,
        customer.goal,
        customer.budget,
        customer.country,
        customer.webinar_join.isoformat() if customer.webinar_join else None,
        customer.webinar_leave.isoformat() if customer.webinar_leave else None,
        customer.engaged_mins,
        customer.asked_question,
        customer.score,
        customer.reasoning,
        customer.status.value if customer.status else None,
        customer.created_at.isoformat(),
        customer.updated_at.isoformat()
    ]

def _row_to_customer(row: List) -> Customer:
    """Convert a CSV row to a Customer object."""
    return Customer(
        id=int(row[0]),
        name=row[1],
        email=row[2],
        phone=row[3],
        address=row[4],
        title=row[5],
        goal=row[6],
        budget=row[7],
        country=row[8],
        webinar_join=datetime.fromisoformat(row[9]) if row[9] else None,
        webinar_leave=datetime.fromisoformat(row[10]) if row[10] else None,
        engaged_mins=int(row[11]) if row[11] else None,
        asked_question=row[12].lower() == 'true',
        score=int(row[13]) if row[13] else None,
        reasoning=row[14],
        status=CustomerStatus(row[15]) if row[15] else None,
        created_at=datetime.fromisoformat(row[16]),
        updated_at=datetime.fromisoformat(row[17])
    )

def _read_all_rows() -> List[List]:
    """Read all rows from the CSV file with thread safety."""
    with _LOCK, open(CSV_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        return list(reader)

def _write_all_rows(rows: List[List]) -> None:
    """Write all rows to the CSV file with thread safety."""
    with _LOCK, open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'name', 'email', 'phone', 'address', 'title', 'goal',
            'budget', 'country', 'webinar_join', 'webinar_leave',
            'engaged_mins', 'asked_question', 'score', 'reasoning',
            'status', 'created_at', 'updated_at'
        ])
        writer.writerows(rows)

def get_all_customers() -> List[Customer]:
    """Get all customers from the CSV file."""
    rows = _read_all_rows()
    return [_row_to_customer(row) for row in rows]

def get_customer_by_id(customer_id: int) -> Optional[Customer]:
    """Get a customer by ID from the CSV file."""
    rows = _read_all_rows()
    for row in rows:
        if int(row[0]) == customer_id:
            return _row_to_customer(row)
    return None

def save_customer(customer: Customer) -> Customer:
    """Save a customer to the CSV file."""
    rows = _read_all_rows()
    customers = [_row_to_customer(row) for row in rows]
    
    # If customer has no ID, assign the next available ID
    if customer.id is None:
        customer.id = max([c.id for c in customers], default=0) + 1
    
    # Update or insert the customer
    customer_exists = False
    for i, c in enumerate(customers):
        if c.id == customer.id:
            customers[i] = customer
            customer_exists = True
            break
    
    if not customer_exists:
        customers.append(customer)
    
    # Write all customers back to CSV
    _write_all_rows([_customer_to_row(c) for c in customers])
    
    return customer

def delete_customer(customer_id: int) -> Optional[Customer]:
    """Delete a customer from the CSV file."""
    rows = _read_all_rows()
    customers = [_row_to_customer(row) for row in rows]
    deleted_customer = None
    
    # Find and remove the customer
    for i, c in enumerate(customers):
        if c.id == customer_id:
            deleted_customer = customers.pop(i)
            break
    
    if deleted_customer:
        # Write remaining customers back to CSV
        _write_all_rows([_customer_to_row(c) for c in customers])
    
    return deleted_customer 