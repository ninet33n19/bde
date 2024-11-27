#!/bin/bash

# Function to run commands in a new Tilix session (pane or tab)
run_in_tilix() {
    tilix --action session-add-right -- bash -c "$1; exec bash"
}

# Terminal 1 commands (first session starts in the default window)
tilix -- bash -c "
conda activate etl &&
docker-compose ps &&
docker-compose up -d &&
docker-compose down -v &&
docker-compose up -d &&
docker-compose ps;
exec bash
"
sleep 2  # Optional delay for stability

# Terminal 2 commands (new pane)
run_in_tilix "
conda activate etl &&
docker cp scripts/init.sql timescaledb:/init.sql &&
docker exec -it timescaledb psql -U admin -d financial_transactions -f /init.sql &&
echo '\dt' | docker exec -it timescaledb psql -U admin -d financial_transactions
"
sleep 2  # Optional delay for stability

# Terminal 3 commands (new pane)
run_in_tilix "
conda activate etl &&
python scripts/kafka_producer.py
"
sleep 10  # Delay of 10 seconds before starting Terminal 4

# Terminal 4 commands (new pane)
run_in_tilix "
conda activate etl &&
python scripts/spark_processor.py
"

# Terminal 5 commands (new pane)
run_in_tilix "
conda activate etl &&
bun run dev
"

