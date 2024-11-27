-- Create the transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    client_id VARCHAR(50),
    card_id VARCHAR(50),
    amount DECIMAL(10,2),
    use_chip BOOLEAN,
    merchant_id VARCHAR(50),
    merchant_city VARCHAR(100),
    merchant_state VARCHAR(2),
    zip VARCHAR(10),
    processing_timestamp TIMESTAMP NOT NULL,
    hour_of_day INTEGER,
    day_of_week INTEGER,
    month INTEGER
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('transactions', 'date');

-- Create indexes for better query performance
CREATE INDEX idx_client_id ON transactions(client_id);
CREATE INDEX idx_merchant_id ON transactions(merchant_id);
CREATE INDEX idx_date ON transactions(date DESC);
