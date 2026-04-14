from kafka import KafkaProducer
import json
import time
import pandas as pd

data = pd.read_csv("nyc_taxi_data.csv")

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = "taxi-data"

for _, row in data.iterrows():
    producer.send(topic, value=row.to_dict())
    time.sleep(0.01)

producer.flush()
print("Data sent to Kafka")
