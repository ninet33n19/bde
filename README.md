# Real-Time Financial Transaction Processing Pipeline

This project demonstrates a real-time data processing pipeline for financial transactions. It uses Kafka for message queuing, Spark Streaming for processing, TimescaleDB for time-series data storage, and Grafana for visualization (though Grafana setup details are not fully in these files). The entire pipeline is orchestrated using Docker Compose.

## Table of Contents

1.  [Core Functionality](#core-functionality)
2.  [Tech Stack & Components](#tech-stack--components)
3.  [Project Structure](#project-structure)
4.  [Setup & Running the Pipeline](#setup--running-the-pipeline)
    *   [Prerequisites](#prerequisites)
    *   [Automated Setup (Using Scripts)](#automated-setup-using-scripts)
    *   [Manual Setup Steps](#manual-setup-steps)
5.  [Key Scripts Explained](#key-scripts-explained)
6.  [Database Schema](#database-schema)
7.  [Notes & Considerations](#notes--considerations)

## Core Functionality

1.  **Data Ingestion:** A Kafka producer reads financial transaction data from a CSV file (`financial_transactions.csv` - assumed to be present) and publishes each transaction as a JSON message to a Kafka topic.
2.  **Stream Processing:** A Spark Streaming application consumes messages from the Kafka topic, parses the JSON, enriches the data (adds processing timestamp, hour of day, day of week, month), and writes the processed data to TimescaleDB.
3.  **Data Storage:** TimescaleDB stores the financial transactions as a hypertable, optimized for time-series data and queries.
4.  **Orchestration:** Docker Compose is used to define and manage all the services (Zookeeper, Kafka, Spark Master/Worker, TimescaleDB, Grafana).
5.  **Automation:** Shell and Python scripts are provided to automate the setup and execution of the different components in separate terminal sessions.

## Tech Stack & Components

*   **Message Queue:** Apache Kafka (Confluent Platform images)
*   **Stream Processing:** Apache Spark (Bitnami Spark image)
    *   Language: Python (PySpark)
*   **Database:** TimescaleDB (PostgreSQL with TimescaleDB extension)
*   **Containerization & Orchestration:** Docker, Docker Compose
*   **Data Producer:** Python script using `kafka-python`
*   **Visualization (Implied):** Grafana
*   **Terminal Multiplexer (for automation):** Tilix
*   **Environment Management:** Conda (implied by `conda activate etl`)

## Project Structure

```
ninet33n19-bde/
├── docker-compose.yml     # Defines and configures all services
├── env_check.py           # Script to check Kafka connectivity (originally for more env checks)
├── run_automation.sh      # Bash script to automate running components in Tilix
├── start_sessions.py      # Python script alternative for automating Tilix sessions
├── temp.md                # Notes/scratchpad for automation script requirements
└── scripts/
    ├── init.sql           # SQL script to initialize TimescaleDB table and hypertable
    ├── kafka_producer.py  # Python script to produce Kafka messages from CSV
    └── spark_processor.py # PySpark script for stream processing
```

## Setup & Running the Pipeline

### Prerequisites

*   Docker and Docker Compose installed.
*   Python 3.x installed with `pip`.
*   Conda (Miniconda/Anaconda) installed for environment management (as scripts use `conda activate etl`).
*   Tilix terminal emulator (if using the automation scripts).
*   A CSV file named `financial_transactions.csv` in the root directory (the Kafka producer expects this).
*   Java Development Kit (JDK) 11 installed and `JAVA_HOME` environment variable set (for Spark). The `spark_processor.py` attempts to set this.

### Automated Setup (Using Scripts)

Two automation scripts are provided: `run_automation.sh` (Bash) and `start_sessions.py` (Python). These scripts are designed to open multiple Tilix terminal sessions and run the necessary commands.

**Using `run_automation.sh`:**

1.  Ensure you have a Conda environment named `etl` with necessary Python packages (like `pyspark`, `kafka-python`, `pandas`, `psycopg2-binary`, `docker`).
2.  Make the script executable: `chmod +x run_automation.sh`
3.  Run the script: `./run_automation.sh`

**Using `start_sessions.py`:**

1.  Ensure you have a Conda environment named `etl` with necessary Python packages.
2.  Install the `docker` and `psycopg2-binary` Python packages: `pip install docker psycopg2-binary`
3.  Run the script: `python start_sessions.py`

These scripts will attempt to:
1.  Start Docker services.
2.  Initialize the TimescaleDB database.
3.  Start the Kafka producer.
4.  Start the Spark processor.
5.  (Optional) Start a development server (`bun run dev` - this seems unrelated to the BDE pipeline itself and might be a leftover or for a separate UI).

### Manual Setup Steps

If not using the automation scripts:

1.  **Start Docker Services:**
    ```bash
    docker-compose up -d
    ```
    (You might need to run `docker-compose down -v && docker-compose up -d` for a clean start as seen in the scripts).

2.  **Initialize Database:**
    Open a terminal:
    ```bash
    conda activate etl # (if you have a conda env)
    docker cp scripts/init.sql ninet33n19-bde-timescaledb-1:/init.sql # Adjust container name if different
    docker exec -it ninet33n19-bde-timescaledb-1 psql -U admin -d financial_transactions -f /init.sql
    ```

3.  **Start Kafka Producer:**
    Open a new terminal:
    ```bash
    conda activate etl # (if you have a conda env)
    python scripts/kafka_producer.py
    ```
    Ensure `financial_transactions.csv` is in the root directory.

4.  **Start Spark Processor:**
    Open another new terminal:
    ```bash
    conda activate etl # (if you have a conda env)
    python scripts/spark_processor.py
    ```

5.  **Access Services:**
    *   **Spark Master UI:** `http://localhost:8080`
    *   **Grafana:** `http://localhost:3000` (admin/admin) - You'll need to configure TimescaleDB as a data source and create dashboards.
    *   **TimescaleDB (psql):**
        ```bash
        docker exec -it ninet33n19-bde-timescaledb-1 psql -U admin -d financial_transactions
        ```

## Key Scripts Explained

*   **`docker-compose.yml`:**
    *   `zookeeper`: Manages Kafka cluster state.
    *   `kafka`: The Kafka message broker. Configured to be accessible from `localhost:9092`.
    *   `spark-master`: Apache Spark master node.
    *   `spark-worker`: Apache Spark worker node connecting to the master.
    *   `timescaledb`: PostgreSQL database with TimescaleDB extension. Persists financial transaction data.
    *   `grafana`: Visualization tool.
*   **`scripts/init.sql`:**
    *   Creates the `transactions` table in TimescaleDB.
    *   Converts `transactions` into a TimescaleDB hypertable partitioned by the `date` column.
    *   Creates indexes for performance.
*   **`scripts/kafka_producer.py`:**
    *   Reads `financial_transactions.csv` using pandas.
    *   Cleans and formats data (date to string, amount to float).
    *   Sends each row as a JSON message to the `financial_transactions` Kafka topic.
*   **`scripts/spark_processor.py`:**
    *   Sets up a SparkSession configured to read from Kafka and write to JDBC (PostgreSQL/TimescaleDB).
    *   Defines a schema for the incoming Kafka messages.
    *   Reads the stream from the `financial_transactions` Kafka topic.
    *   Parses the JSON value from Kafka messages.
    *   Enriches the data by adding `processing_timestamp`, `hour_of_day`, `day_of_week`, and `month`.
    *   Writes the processed DataFrame to the `transactions` table in TimescaleDB in append mode using JDBC.
*   **`run_automation.sh` & `start_sessions.py`:**
    *   Automate the process of setting up the environment and running the different components in separate Tilix terminal windows/panes. They handle Docker commands, database initialization, and starting the producer/processor.
*   **`env_check.py`:**
    *   Currently, this script only checks Kafka connectivity. The commented-out code suggests it was intended for more comprehensive environment checks (Python, Java, PySpark).

## Database Schema

Table: `transactions` (in TimescaleDB `financial_transactions` database)
*   `id` (INTEGER, PRIMARY KEY)
*   `date` (TIMESTAMP, Hypertable time dimension)
*   `client_id` (VARCHAR(50))
*   `card_id` (VARCHAR(50))
*   `amount` (DECIMAL(10,2))
*   `use_chip` (BOOLEAN)
*   `merchant_id` (VARCHAR(50))
*   `merchant_city` (VARCHAR(100))
*   `merchant_state` (VARCHAR(2))
*   `zip` (VARCHAR(10))
*   `processing_timestamp` (TIMESTAMP) - Added by Spark
*   `hour_of_day` (INTEGER) - Added by Spark
*   `day_of_week` (INTEGER) - Added by Spark
*   `month` (INTEGER) - Added by Spark

Indexes are created on `client_id`, `merchant_id`, and `date`.

## Notes & Considerations

*   **`financial_transactions.csv`:** This file is crucial for the Kafka producer to run. It's not included in the provided structure, so it must be obtained or created.
*   **Conda Environment `etl`:** The automation scripts assume a Conda environment named `etl` exists and is activated. This environment should have `pyspark`, `kafka-python`, `pandas`, `psycopg2-binary`, and `docker` (for `start_sessions.py`).
*   **Tilix Dependency:** The automation scripts rely on the Tilix terminal emulator. If you use a different terminal, you'll need to adapt these scripts.
*   **`JAVA_HOME`:** The `spark_processor.py` script attempts to set `JAVA_HOME`. Ensure this path (`/usr/lib/jvm/java-11-openjdk-amd64`) is correct for your Spark Docker image or your local system if running Spark locally.
*   **`bun run dev` in `run_automation.sh`:** This command seems out of place for a big data pipeline focused on Kafka/Spark. It might be a leftover from another project or intended for a separate UI component not detailed here.
*   **Error Handling:** The Spark processor includes some `try-except` blocks for basic error handling during stream writing.
*   **Grafana Configuration:** The `docker-compose.yml` starts Grafana, but dashboard setup (connecting to TimescaleDB, creating visualizations) would need to be done manually through the Grafana UI at `http://localhost:3000`.
