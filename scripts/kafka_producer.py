from kafka import KafkaProducer
import pandas as pd
import json
import time


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"], value_serializer=json_serializer
)

# Read CSV file
df = pd.read_csv("financial_transactions.csv")

# Convert date column to datetime and then to string
df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d %H:%M:%S")

# Clean amount column by removing '$' and converting to float
df["amount"] = df["amount"].str.replace("$", "").astype(float)


# Process and send each row to Kafka
def send_to_kafka():
    for _, row in df.iterrows():
        data = {
            "id": int(row["id"]),
            "date": str(row["date"]),  # Already converted to string above
            "client_id": str(row["client_id"]),
            "card_id": str(row["card_id"]),
            "amount": float(row["amount"]),
            "use_chip": bool(row["use_chip"]),
            "merchant_id": str(row["merchant_id"]),
            "merchant_city": str(row["merchant_city"]),
            "merchant_state": str(row["merchant_state"]),
            "zip": str(row["zip"]),
        }

        # Send to Kafka topic
        producer.send("financial_transactions", value=data)
        print(f"Sent transaction for the date {data['date']} to Kafka")
        # time.sleep(0.1)  # Add small delay to simulate real-time data


if __name__ == "__main__":
    send_to_kafka()
    producer.flush()
