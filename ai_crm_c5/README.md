# 100xEngineers CRM with Supabase

A Streamlit-based CRM application integrated with Supabase for data persistence and management.

## Features

- **Customer Management**: Create, read, update, and delete customer records
- **Lead Qualification**: AI-powered lead scoring using Groq LLM
- **Authentication**: Simple login system for secure access
- **Real-time Data**: All data is stored in Supabase for persistence
- **Webinar Tracking**: Track customer engagement during webinars
- **Filtering**: Filter customers by qualification status

## Setup

### 1. Environment Variables

Create a `.env` file in the `ai_crm_c5` directory with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Authentication (optional - defaults provided)
ADMIN_EMAIL=admin@100xengineers.com
ADMIN_PASSWORD=admin123

# Optional: Groq API for lead qualification
GROQ_API_KEY=your_groq_api_key
```

### 2. Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Get your project URL and anon key from the project settings
3. Run the SQL migration script to create the customers table:

```sql
-- Run the contents of migrations/create_customers_table.sql in your Supabase SQL editor
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run ui.py
```

## Database Schema

The application uses a `customers` table with the following structure:

- `id`: Primary key (auto-increment)
- `name`: Customer name (required)
- `email`: Customer email (required, unique)
- `phone`: Phone number (optional)
- `country`: Country (optional)
- `goal`: Customer's goal (optional)
- `budget`: Budget type (Self/Company)
- `webinar_join`: Webinar join timestamp
- `webinar_leave`: Webinar leave timestamp
- `asked_q`: Boolean - asked questions during webinar
- `referred`: Boolean - customer was referred
- `past_touchpoints`: Number of past interactions
- `engaged_mins`: Calculated engagement time
- `score`: AI-generated qualification score
- `reasoning`: AI-generated qualification reasoning
- `status`: Qualification status (Qualified/Nurture)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

## Authentication

The application uses a simple authentication system. Default credentials:
- Email: admin@100xengineers.com
- Password: admin123

You can change these by setting the `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables.

## Lead Qualification

The application includes an AI-powered lead qualification system that:
- Analyzes customer engagement during webinars
- Considers customer goals and budget
- Generates a score from 0-100
- Provides detailed reasoning for the qualification
- Uses Groq's Llama3 model (optional - falls back to simplified scoring)

## File Structure

```
ai_crm_c5/
├── ui.py                 # Main Streamlit application
├── supabase_service.py   # Supabase database operations
├── auth.py              # Authentication management
├── config.py            # Supabase configuration
├── requirements.txt     # Python dependencies
├── migrations/          # Database migration scripts
│   └── create_customers_table.sql
└── README.md           # This file
```

## Usage

1. **Login**: Use the provided credentials to access the application
2. **View Customers**: Browse all customers with filtering options
3. **Add Customer**: Create new customer records
4. **Update Customer**: Modify existing customer information
5. **Delete Customer**: Remove customer records
6. **Qualify Customer**: Run AI-powered lead qualification

## Error Handling

The application includes comprehensive error handling for:
- Database connection issues
- Authentication failures
- Data validation errors
- API call failures

All errors are displayed to the user with helpful messages.

## Security

- Row Level Security (RLS) is enabled on the customers table
- Authentication is required for all operations
- Environment variables are used for sensitive configuration
- Input validation is performed on all user inputs

