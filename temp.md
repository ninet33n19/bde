i want to create an automation script in different terminal sessions that performs the following sequence of commands:

remeber to run 'conda activate etl' in every terminal session

Terminal 1:
1. docker-compose ps
2. docker-compose up -d
3. docker-compose down -v
4. docker-compose up -d
5. docker-compose ps

Terminal 2:
1. docker cp scripts/init.sql timescaledb:/init.sql
2. docker exec -it timescaledb psql -U admin -d financial_transactions -f /init.sql
3. \dt

Terminal 3:
1. py scripts/kafka_producer.py

Terminal 4:
1. py scripts/spark_processor.py

Terminal 5:
1. bun run dev


