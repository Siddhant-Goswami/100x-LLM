# AI Bootcamp Customer Qualification API

This API provides endpoints for managing and qualifying customers for a 6-month applied AI bootcamp using Groq's LLM capabilities.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export GROQ_API_KEY=your_groq_api_key
```

3. Run the API:
```bash
uvicorn ai_crm.main:app --reload
```

## API Endpoints

### Customer Management

#### Create and Qualify Customer
```http
POST /customers
```
Creates a new customer and automatically qualifies it using the LLM-based scoring system.

Request body:
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "title": "Senior ML Engineer",
    "goal": "Lead AI team",
    "budget": "company",
    "country": "US",
    "asked_question": true
}
```

#### Get All Customers
```http
GET /customers
```
Returns a list of all customers.

#### Get Sales Qualified Customers
```http
GET /customers/qualified
```
Returns a list of all sales qualified customers (those with a score >= 70).

#### Get Customer by ID
```http
GET /customers/{customer_id}
```
Returns a specific customer by ID.

#### Update Customer
```http
PUT /customers/{customer_id}
```
Updates a customer and re-qualifies it.

#### Delete Customer
```http
DELETE /customers/{customer_id}
```
Deletes a customer.

#### Re-qualify Customer
```http
POST /customers/{customer_id}/requalify
```
Re-qualifies an existing customer using the current data.

## Customer Scoring Rubric

The customer qualification system uses the following rubric weights:
- Role seniority (15 points)
- Tech background (15 points)
- Goal alignment (15 points)
- Budget (10 points)
- Urgency (10 points)
- Webinar engagement (10 points)
- Question activity (7 points)
- Country/Timezone (6 points)
- Referral source (6 points)
- Past touchpoints (6 points)

Customers scoring ≥70 are marked as SQL (Sales Qualified), while customers scoring <70 are marked for nurturing.

## Engagement Scoring

Webinar engagement is scored based on duration:
- 0-5 minutes: 0 points
- 6-20 minutes: 0.3 points
- 21-40 minutes: 0.6 points
- 40+ minutes: 1.0 points 