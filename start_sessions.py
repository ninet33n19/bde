import subprocess
import time
import os

try:
    import docker
except ImportError:
    print("Docker package not installed. Please run: pip install docker")
    exit(1)
import psycopg2
from pathlib import Path


def wait_for_docker_services():
    """Wait for Docker services to be ready"""
    client = docker.from_env()
    retries = 30
    while retries > 0:
        try:
            containers = client.containers.list()
            all_ready = all(container.status == "running" for container in containers)
            if all_ready:
                return True
        except Exception as e:
            print(f"Error checking Docker services: {str(e)}")
        time.sleep(2)
        retries -= 1
    return False


def wait_for_database():
    """Wait for TimescaleDB to be ready"""
    retries = 30
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname="financial_transactions",
                user="admin",
                password="admin",
                host="localhost",
                port="5432",
            )
            conn.close()
            return True
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
        time.sleep(2)
        retries -= 1
    return False


def create_command_script(commands, script_name):
    """Create a temporary shell script with the given commands"""
    with open(script_name, "w") as f:
        f.write("#!/usr/bin/env zsh\n")
        f.write("source ~/.zshrc\n")
        f.write("conda activate etl\n")
        for cmd in commands:
            f.write(f"{cmd}\n")
        f.write('read "?Press Enter to close..."\n')
    os.chmod(script_name, 0o755)


def launch_terminal(commands, terminal_num, wait_condition=None):
    """Launch a terminal with commands and optional wait condition"""
    script_name = f"/tmp/terminal{terminal_num}_commands.sh"
    create_command_script(commands, script_name)

    if wait_condition:
        if not wait_condition():
            print(f"Wait condition failed for terminal {terminal_num}")
            return False

    try:
        subprocess.Popen(["tilix", "-e", "zsh", script_name])
        time.sleep(2)  # Basic delay between terminal launches
        return True
    except FileNotFoundError:
        print("Could not find tilix. Please ensure it is installed.")
        return False


def main():
    # Define commands for each terminal
    terminal1_commands = [
        "docker-compose ps",
        "docker-compose up -d",
        "docker-compose down -v",
        "docker-compose up -d",
        "docker-compose ps",
    ]

    terminal2_commands = [
        "docker cp scripts/init.sql timescaledb:/init.sql",
        "docker exec -it timescaledb psql -U admin -d financial_transactions -f /init.sql",
        "\\dt",
    ]

    terminal3_commands = ["py scripts/kafka_producer.py"]
    terminal4_commands = ["py scripts/spark_processor.py"]
    terminal5_commands = ["bun run dev"]

    # Launch terminals sequentially with dependencies
    terminals = [
        (terminal1_commands, None),  # No wait condition for first terminal
        (terminal2_commands, wait_for_docker_services),  # Wait for Docker services
        (terminal3_commands, wait_for_database),  # Wait for database
        (
            terminal4_commands,
            lambda: Path("scripts/kafka_producer.py").exists(),
        ),  # Wait for Kafka producer
        (
            terminal5_commands,
            lambda: Path("scripts/spark_processor.py").exists(),
        ),  # Wait for Spark processor
    ]

    for i, (commands, wait_condition) in enumerate(terminals, 1):
        success = launch_terminal(commands, i, wait_condition)
        if not success:
            print(f"Failed to launch terminal {i}")
            break

    # Clean up temporary scripts after a delay
    time.sleep(5)
    for i in range(1, 6):
        try:
            os.remove(f"/tmp/terminal{i}_commands.sh")
        except OSError as e:
            print(f"Error removing temporary script {i}: {e}")


if __name__ == "__main__":
    main()
