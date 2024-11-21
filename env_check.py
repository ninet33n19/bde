# import os
# import sys
# import subprocess


# def check_environment():
#     # Check Python version
#     print(f"Python version: {sys.version}")

#     # Check Java version
#     try:
#         java_version = subprocess.check_output(
#             ["java", "-version"], stderr=subprocess.STDOUT
#         ).decode()
#         print(f"Java version: {java_version}")
#     except:
#         print("Java not found! Please install Java 11")
#         return False

#     # Check JAVA_HOME
#     java_home = os.environ.get("JAVA_HOME")
#     print(f"JAVA_HOME: {java_home}")

#     # Check PySpark installation
#     try:
#         import pyspark

#         print(f"PySpark version: {pyspark.__version__}")
#     except ImportError:
#         print("PySpark not found! Please install pyspark")
#         return False

#     return True


# if __name__ == "__main__":
#     if check_environment():
#         print("Environment check passed!")
#     else:
#         print("Environment check failed! Please fix the issues above.")

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="test-group",
)
print("Connected to Kafka" if consumer.bootstrap_connected() else "Failed to connect")
