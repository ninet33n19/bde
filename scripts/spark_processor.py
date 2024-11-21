import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json,
    col,
    current_timestamp,
    hour,
    dayofweek,
    month,
)
from pyspark.sql.types import (
    StructField,
    StructType,
    IntegerType,
    TimestampType,
    StringType,
    DoubleType,
    BooleanType,
)

# Set Java Home
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"

# Initialize Spark Session with updated configurations
spark = (
    SparkSession.builder.appName("FinancialTransactionsProcessor")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,"
        "org.apache.kafka:kafka-clients:2.8.0,"
        "org.postgresql:postgresql:42.2.23",  # Add PostgreSQL driver
    )
    .config("spark.driver.extraJavaOptions", "-XX:+UseG1GC")
    .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC")
    .config("spark.driver.memory", "2g")
    .config("spark.executor.memory", "2g")
    .config("spark.sql.adaptive.enabled", "true")
    .master("local[*]")
    .getOrCreate()
)

# Set log level to reduce verbosity
spark.sparkContext.setLogLevel("WARN")

# Define schema for the incoming data
schema = StructType(
    [
        StructField("id", IntegerType()),
        StructField("date", TimestampType()),
        StructField("client_id", StringType()),
        StructField("card_id", StringType()),
        StructField("amount", DoubleType()),
        StructField("use_chip", BooleanType()),
        StructField("merchant_id", StringType()),
        StructField("merchant_city", StringType()),
        StructField("merchant_state", StringType()),
        StructField("zip", StringType()),
    ]
)

try:
    # Read from Kafka
    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "financial_transactions")
        .option("startingOffsets", "earliest")
        .load()
    )

    # Parse JSON data
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("parsed_data")
    ).select("parsed_data.*")

    # Add processing timestamp
    processed_df = parsed_df.withColumn("processing_timestamp", current_timestamp())

    # Calculate additional metrics
    enriched_df = (
        processed_df.withColumn("hour_of_day", hour("date"))
        .withColumn("day_of_week", dayofweek("date"))
        .withColumn("month", month("date"))
    )

    # Write to TimescaleDB with updated JDBC configuration
    def write_to_timescaledb(df, epoch_id):
        try:
            # Replace 'nan' with None
            df = df.replace("nan", None)

            df.write.format("jdbc").option("driver", "org.postgresql.Driver").option(
                "url", "jdbc:postgresql://localhost:5432/financial_transactions"
            ).option("dbtable", "transactions").option("user", "admin").option(
                "password", "password"
            ).option("stringtype", "unspecified").mode("append").save()

            print(f"Batch {epoch_id}: Written {df.count()} records to TimescaleDB")
        except Exception as e:
            print(f"Error writing to TimescaleDB: {str(e)}")

    # Start the streaming query with error handling and monitoring
    query = (
        enriched_df.writeStream.foreachBatch(write_to_timescaledb)
        .outputMode("append")
        .trigger(processingTime="5 seconds")
        .start()
    )

    # Monitor query progress and errors
    try:
        query.awaitTermination()
    except Exception as e:
        print(f"Streaming query failed: {str(e)}")
        query.stop()

except Exception as e:
    print(f"Error in Spark processing: {str(e)}")
    spark.stop()
