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

-- Create materialized views for common aggregations
CREATE MATERIALIZED VIEW hourly_stats AS
SELECT
    time_bucket('1 hour', date) AS bucket,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    merchant_state
FROM transactions
GROUP BY bucket, merchant_state
WITH NO DATA;

-- Refresh policy for materialized view
SELECT add_continuous_aggregate_policy('hourly_stats',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
