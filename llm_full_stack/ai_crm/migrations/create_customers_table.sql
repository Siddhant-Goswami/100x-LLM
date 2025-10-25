-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    country TEXT,
    goal TEXT,
    budget TEXT,
    webinar_join TIMESTAMP WITH TIME ZONE,
    webinar_leave TIMESTAMP WITH TIME ZONE,
    asked_q BOOLEAN DEFAULT FALSE,
    referred BOOLEAN DEFAULT FALSE,
    past_touchpoints INTEGER DEFAULT 0,
    engaged_mins FLOAT,
    score FLOAT,
    reasoning TEXT,
    status TEXT CHECK (status IN ('Qualified', 'Nurture')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on email for faster lookups
CREATE INDEX IF NOT EXISTS customers_email_idx ON customers(email);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 